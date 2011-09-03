'''
8/08/08 UPDATE - Imports BVH skeleton into Model path
8/09/08 UPDATE - Creates bind pose at Frame -5
8/09/08 UPDATE - Zero Length Bone crashes exporter; hacked solution
'''
import win32com.client
from win32com.client import constants

class mt_Global:
	'''
	mt_Global class can be used as an object to contain variables your app needs pass and write to.
	'''
	def Model_Space():
		pass
	def JointList():
		pass
	def XformList():
		pass
	def KeyFrameList():
		pass
	def FrameCount():
		pass
	def FrameRate():
		pass
	def Temp_List():
		pass
	def Temp_Pos():
		pass
	def Temp_String():
		pass
	def Error_Bone():
		pass

class BVH_Joint :
	'''
	FOR RIG SETUP:
	BVH_Joint class - Stores names of joints, their parents, and their world space offsets.  Use
	'self.echo' to print current values.
	'''
	def __init__(self, name ='', parent ='', offset =[0,0,0]):
		self.name = name
		self.parent = parent
		self.vector = XSIMath.CreateVector3(offset)
	
	def echo(self):
		Application.Logmessage('%.2f %.2f %.2f' %(self.vector.X, self.vector.Y, self.vector.Z))
		
class BVH_Xform:
	'''
	FOR ANIMATION:
	BVH_Xform class - Stores names of animatable joints, and index of Xform channels.  To 
	print value use 'self.echo'.
	'''
	def __init__(self, name ='', index=[]):
		
		self.name = name
		self.index = index # Look-up for which channel to add each value

	def echo(self):
		Application.Logmessage('BVH_XFORM: name - " %s " | index - " %s "' %(self.name, self.index))

class BVH_Frame:
	'''
	KEYFRAMES:
	BVH_Frame class - A list to store one frame's worth of data.  To print value use 'self.echo'.
	'''
	def __init__(self, value =[]):
		self.value = value
		
	def echo(self):
		Application.Logmessage('BVH_FRAME: value - %.2f' %(self.value))
		
def mt_BVH_Main():
	'''
	This script imports a *.BVH motion file by:
		1) Processing the commands to generate a skeleton
		2) Applies animation to that skeleton
	'''
	mt_Global.KeyFrameList = []
	mt_Global.JointList = []
	mt_Global.XformList = []
	mt_Global.Temp_List = []
	mt_Global.Temp_Pos = [0,0,0]
	
	LineID = 0			# Tracks the line count into the *.BVH file
	Switch_ID = -1		# Determines whether skeleton or animation data's being collected; -1:skeleton, 0:animation
	
	f = file(mt_SelectTextFile())
	while True:
		line_input = f.readline()
		if len(line_input) == 0:
			break
		else:
				# Reading in and Tokenizing
			TokenLine = line_input.split()
		if TokenLine[0] != 'HIERARCHY' and LineID == 0: # Quick check to see if loaded file is formatted correctly 
			Application.Logmessage("First line != 'HIERARCHY'; this isn't a standard *.BVH file.")
			break
		if Switch_ID == -1:
			if TokenLine[0] == 'MOTION':
			
					# Build Skeleton
				mt_BuildSkeleton(mt_Global.JointList, mt_Global.XformList)
				
					# Get Frame Count
				line_input = f.readline()
				TokenLine = line_input.split()
				if TokenLine[0] == 'Frames:' :
					mt_Global.FrameCount = int(TokenLine[1])
				LineID = LineID + 1
				
					# Get Frame Rate
				line_input = f.readline()
				TokenLine = line_input.split()
				if TokenLine[0] == 'Frame' :
					mt_Global.FrameRate = TokenLine[2]
				LineID = LineID + 1
				
					# Advance to Key Frames
				line_input = f.readline()
				TokenLine = line_input.split()
				LineID = LineID + 1
						
				Switch_ID = 0		# '-1' = Skeleton Setup | '0' = Apply Animation : Switching to animation mode
			else:
					# Collecting Joint Info
				mt_GetJointInfo(TokenLine)
		if Switch_ID == 0:
				# Collecting Animation Info
			mt_Global.KeyFrameList.append(BVH_Frame([]))
			mt_GetAnimationInfo(TokenLine)
		LineID = LineID + 1
	Application.Logmessage('Reached End-of-File, now closing document.')
	f.close
	mt_SetPlayBack()
	mt_ApplyAnimation(mt_Global.XformList, mt_Global.KeyFrameList)
	Application.Logmessage('Animation applied, BVH import complete!')
	if (mt_Global.Error_Bone == 1):
		Application.Logmessage('BUT SOME BONES WERE MODIFIED: ELSE XSI crashes on Bones with Zero Length')

def mt_SetPlayBack():
	'''
	Sets playback rate and range.
	'''

	Application.SetValue('PlayControl.Out', mt_Global.FrameCount) # Set Frame Count(Range)
		# Set Frame Rate
	if mt_Global.FrameRate == '0.033333':
		Application.SetValue('PlayControl.Rate', 30)
	elif mt_Global.FrameRate == '0.016667':
		Application.SetValue('PlayControl.Rate', 60)
	elif mt_Global.FrameRate == '0.066667':
		Application.SetValue('PlayControl.Rate', 15)
	else:
		mt_Global.FrameRate = 'default - NTSC(29.97 fps)'
		Application.SetValue('PlayControl.Format', 10)	# NTSC(29.97fps) 
	
def mt_ApplyAnimation(XformList, KeyFrames):
	'''
	Applies keyframes to a given XformList.
	'''
	
		# Apply Animation
	for k in range(0, len(KeyFrames)):
		counter = 0
		for x in range(0, len(XformList)):
			CurrentJoint = mt_Global.Model_Space.FindChild(str(XformList[x].name))
			for v in range(0, len(XformList[x].index)):
				if XformList[x].index[v] == 'rotX':
					mt_FCurve = CurrentJoint.rotx.Source
					mt_FCurve.AddKey(k+1, KeyFrames[k].value[counter])
				if XformList[x].index[v] == 'rotY':
					mt_FCurve = CurrentJoint.roty.Source
					mt_FCurve.AddKey(k+1, KeyFrames[k].value[counter])
				if XformList[x].index[v] == 'rotZ':
					mt_FCurve = CurrentJoint.rotz.Source
					mt_FCurve.AddKey(k+1, KeyFrames[k].value[counter])
				if XformList[x].index[v] == 'posX':
					mt_FCurve = CurrentJoint.posx.Source
					mt_FCurve.AddKey(k+1, KeyFrames[k].value[counter])
				if XformList[x].index[v] == 'posY':
					mt_FCurve = CurrentJoint.posy.Source
					mt_FCurve.AddKey(k+1, KeyFrames[k].value[counter])
				if XformList[x].index[v] == 'posZ':
					mt_FCurve = CurrentJoint.posz.Source
					mt_FCurve.AddKey(k+1, KeyFrames[k].value[counter])
				counter = counter + 1
		
def mt_GetAnimationInfo(InputList):
	'''
	Grabs keyframes data and adds to the Global_KeyFrameList.
	'''

	for i in range(0, len(InputList)):
		mt_Global.KeyFrameList[-1].value.append(float(InputList[i]))
		
def mt_GetJointInfo(InputList):
	'''
	Collects BVH_JointInfo from a given line.
	'''

	for i in range(0, len(InputList)):
	
		if InputList[i] == 'ROOT'		:
			mt_Global.Temp_String = InputList[i +1]
			Temp_Tuple = ('Scene_Root', mt_Global.Temp_Pos)
			mt_Global.Temp_List.append(Temp_Tuple)
			break
			
		if InputList[i] == 'OFFSET'		:						# Joint Position Found
			JPosOffset = [float(InputList[i +1]), float(InputList[i +2]), float(InputList[i +3])]
			
			if(JPosOffset[0] == 0):		#ALERT:  XSI crashes if bone length = 0
				if(JPosOffset[1] == 0):
					if(JPosOffset[2] == 0):
						JPosOffset[0] += 1
						mt_Global.Error_Bone = 1	#Alert user that bone postion was altered at the end of process

			mt_Global.Temp_Pos = mt_Global.Temp_List[-1][1]
			Buffer_x = JPosOffset[0] + mt_Global.Temp_Pos[0]
			Buffer_y = JPosOffset[1] + mt_Global.Temp_Pos[1]
			Buffer_z = JPosOffset[2] + mt_Global.Temp_Pos[2]
			mt_Global.Temp_Pos = [Buffer_x, Buffer_y, Buffer_z]
			mt_Global.JointList.append(BVH_Joint(mt_Global.Temp_String, mt_Global.Temp_List[-1][0], mt_Global.Temp_Pos))
			Temp_Tuple = (mt_Global.Temp_String, mt_Global.Temp_Pos)
			mt_Global.Temp_List.append(Temp_Tuple)
			break
			
		if InputList[i] == 'JOINT'		:						# Joint name found
			mt_Global.Temp_String = InputList[i +1]
			break
			
		if InputList[i] == '}'			:						# Remove entry from ParentList
			mt_Global.Temp_List.remove(mt_Global.Temp_List[-1])	# PYTHON : List[-1] = List[len(List)] (negative index counts backwards)
			break
			
		if InputList[i] == 'CHANNELS'	:						# Channel Information
			mt_Global.XformList.append(BVH_Xform(name = mt_Global.Temp_String, index = []))
			Num_Channels = int(InputList[i+1])
			for j in range(2, Num_Channels+2):
				if InputList[j] == 'Xrotation':
					mt_Global.XformList[-1].index.append('rotX')
				if InputList[j] == 'Yrotation':
					mt_Global.XformList[-1].index.append('rotY')
				if InputList[j] == 'Zrotation':
					mt_Global.XformList[-1].index.append('rotZ')
				if InputList[j] == 'Xposition':
					mt_Global.XformList[-1].index.append('posX')
				if InputList[j] == 'Yposition':
					mt_Global.XformList[-1].index.append('posY')
				if InputList[j] == 'Zposition':
					mt_Global.XformList[-1].index.append('posZ')

def mt_BuildSkeleton(JointList, XformList):
	'''
	Takes a BVH_Joint List and builds a rig.  Utilizes XformList to initialize rotation and position
	channels.
	'''
	
	end = len(JointList)
	JointList.append(JointList[0]) # To wrap around, first Joint entry is appended to end
	for i in range(0, end):
	
		EndJoint_ID = -1
		Pos_Root = JointList[i].vector
		Pos_Eff = JointList[i+1].vector
		
		if JointList[i].name != JointList[i].parent:
			mt_Make_Joint(Pos_Root, Pos_Eff, JointList[i].name, JointList[i].parent)			
		if JointList[i].name == JointList[i].parent: 
			EndJoint_ID = 1 			# '1' = End of Chain Found 
			
		mt_DisplaySetup_Joint(JointList[i].name, EndJoint_ID)
	
	for i in range(0, len(mt_Global.XformList)):
		mt_Create_FCurve_on_XformChannels(mt_Global.XformList[i].name, len(mt_Global.XformList[i].index))

def mt_Make_Joint(Input_Pos_Root, Input_Pos_Eff, Input_Joint, Input_Joint_Parent):
	'''
	Builds a Joint in XSI.
	'''

	Def_ChainNormalPlane = XSIMath.CreateVector3(0, 0, 1) # Default value for ChainNormal Plance, xsi.add3dchain fails unless this argument is explicitly defined
	
	if Input_Joint_Parent == 'Scene_Root':
		Return_Joint = mt_Global.Model_Space.Add3DChain(Input_Pos_Root, Input_Pos_Eff, Def_ChainNormalPlane, Input_Joint)
	if Input_Joint_Parent != 'Scene_Root':
		jParent = mt_Global.Model_Space.FindChild(str(Input_Joint_Parent))
		Return_Joint = jParent.Add3DChain(Input_Pos_Root, Input_Pos_Eff, Def_ChainNormalPlane, Input_Joint)

	Application.SetValue(str(Return_Joint) + '.kine.local.rotorder', 2)
	return Return_Joint
	
def mt_DisplaySetup_Joint(BVH_Joint, Switch_ID):
	'''
	Describes how a Joint is displayed in XSI : size, root + end effector icons...etc
	'''

	oRoot = mt_Global.Model_Space.FindChild(str(BVH_Joint))
	tempJoint_mt = oRoot.FindChild()
	tempJoint_End_mt = oRoot.Effector
	Application.SetValue(str(oRoot) + '.root.primary_icon', 5)
	Application.SetValue(str(oRoot) + '.root.size', 2)
	tempJoint_mt.Name = 'bone_' + str(BVH_Joint)
	Application.SetValue(str(tempJoint_mt) + '.bone.size', 3)

	if Switch_ID > 0:
		tempJoint_End_mt.Name = 'End_Site_' + str(BVH_Joint)
		Application.SetValue(str(tempJoint_End_mt) + '.eff.primary_icon', 4)
		Application.SetValue(str(tempJoint_End_mt) + '.eff.size', 2)
	if Switch_ID < 0:
		Application.Logmessage(tempJoint_End_mt.Name)
		tempJoint_End_mt.Name = 'eff_' + str(BVH_Joint)
		Application.SetValue(str(tempJoint_End_mt) + '.eff.primary_icon', 0)
		
def mt_Create_FCurve_on_XformChannels(BVH_Joint_Animatable, BVH_Xform_channelNum):
	'''
	Assigns empty Fcurves to XformChannels in XSI.
	'''

	oFCurve_mt = mt_Global.Model_Space.FindChild(str(BVH_Joint_Animatable))
	
	if BVH_Xform_channelNum == 3:		# BVH_Xform_channelNum = 3 : 'joint' type, 6 : 'root' type
		mt_FCurve = oFCurve_mt.rotx.AddFCurve2()
		mt_FCurve.AddKey(-5)
		mt_FCurve = oFCurve_mt.roty.AddFCurve2()
		mt_FCurve.AddKey(-5)
		mt_FCurve = oFCurve_mt.rotz.AddFCurve2()
		mt_FCurve.AddKey(-5)
		
	if BVH_Xform_channelNum == 6:
		mt_FCurve = oFCurve_mt.rotx.AddFCurve2()
		mt_FCurve.AddKey(-5)
		mt_FCurve = oFCurve_mt.roty.AddFCurve2()
		mt_FCurve.AddKey(-5)
		mt_FCurve = oFCurve_mt.rotz.AddFCurve2()
		mt_FCurve.AddKey(-5)
		mt_FCurve = oFCurve_mt.posx.AddFCurve2()
		mt_FCurve.AddKey(-5)
		mt_FCurve = oFCurve_mt.posy.AddFCurve2()
		mt_FCurve.AddKey(-5)
		mt_FCurve = oFCurve_mt.posz.AddFCurve2()
		mt_FCurve.AddKey(-5)

def mt_SelectTextFile():
	'''
	This function allows a user to select a file to open, by accessing the XSIUIToolkit object.
	This particular implementation is set to filter 'Biovision Hierarchal Data'.
	To call this help doc, use ' Application.logmessage(mt_SelectTextFile.__doc__) '
	'''

		# Simple Python script that shows how to use the XSIUIToolkit object.
	oFileBrowser = XSIUIToolkit.FileBrowser

		# Set the title, initial directory and filter
	oFileBrowser.DialogTitle = 'Select a file'
	oFileBrowser.InitialDirectory = '\\\\INSERT\YOUR\DEFAULT\DIRECTORY\HERE\\'
	oFileBrowser.Filter = 'Biovision hierarchial data (*.bvh)|*.bvh||'

		# Show an open file dialog
	oFileBrowser.ShowOpen()
	
		# Error Feedback
	if oFileBrowser.FilePathName != '':
		Application.Logmessage('User selected ' + str(oFileBrowser.FilePathName))
		mt_Global.Model_Space = Application.ActiveProject.ActiveScene.Root.AddModel("", str(oFileBrowser.FileBaseName)) #Get the Model Space
	else:
		Application.Logmessage('User pressed cancel')
	
	return oFileBrowser.FilePathName
		
mt_BVH_Main()
	
