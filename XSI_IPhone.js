//	07/16/09
//
//	--This scipt--|
//			 --exports direct X file--
//			 --collects vertices, face, normals and texture coord info from resulting text
//			 --writes out to an OpenGL ready format suitable for devices like the IPhone
//				--tested on Jeff LaMarche framework:   http://innerloop.biz/code/Empty%20OpenGL%20ES%20Application.zip
//			
//	--Mike Ton - mike.ton@gmail.com

var fso = new ActiveXObject("Scripting.FileSystemObject");
var filepathMT = XSIUtils.BuildPath(Application.InstallationPath(siProjectPath), "Models");

	//File browser - For user to specify resulting file name
var oUIToolkit = new ActiveXObject("XSI.UIToolKit");
var oFileBrowser = oUIToolkit.FileBrowser;
	oFileBrowser.InitialDirectory = filepathMT;
	oFileBrowser.Filter = "IPhone/OpenGL (*.h)|*.*||" ;
	oFileBrowser.ShowSave();
	
	if(oFileBrowser.FilePathName == "")
		logmessage("Export Cancelled.", siWarning);
	else{
		var filepathMT = oFileBrowser.FilePathName;
		logmessage("Exporting to : " + filepathMT);
		var token = filepathMT.split(/[\\]/);
		var obj3D_Name = token[token.length - 1];
			//Handles if user includes ".x" extension
		if(obj3D_Name.match(/(.x)$/) == null)
			filepathMT = filepathMT + ".x";
		else
			obj3D_Name = obj3D_Name.replace(".x", "");
			//export to intermediate file format : DirectX
		DXExport( filepathMT, 
				   0,     // format type
				   false,  // export anim
				   1,     // frame offset 
				   0,  // type - 0 for Matrix keys, 1 for SRTs
				   true, // import textures
				   false, // absolute paths
				   false, // image sequences
				   false, // copy textures
				   0,     // Resize X - 0 for don't resize, 1 for auto, ...
				   0,     // Resize Y - 0 for don't resize, 1 for auto, ...
				   0,     // Image format - 0 for original, ...
				   true,  // triangulate
				   false,  // plot animation
				   false,  // export hidden objects
				   0,
				   true      // compress mesh
		);
			
			//array of data to be exported to iphone/OpenGL format
		var numVerts = 0;
		var vertArrays = new Array();
		var numFaces = 0;
		var faceArrays = new Array();
		var numNormals = 0;
		var normArrays = new Array();
		var numUVs = 0;
		var uvArrays = new Array();
			
		var ts = fso.OpenTextFile(filepathMT, 1);	//1 = "ForReading"
		var line = ts.ReadLine();
		while(!ts.AtEndofStream)
		{
			var line = ts.ReadLine();
			var token = line.split(/ /);
			if(token[0] == "Mesh")
			{
					//Getting Vertex Array
				line = ts.ReadLine();
				numVerts = parseInt(line.split(/[^0-9]/));
				for(var i = 0; i < numVerts; i++){
					line = ts.ReadLine().split(/[;,]/);
					for(var j = 0; j < line.length; j++)
						vertArrays.push(line[j]);
				}
					//Getting Face Index Array
				line = ts.ReadLine();
				numFaces = parseInt(line.split(/[^0-9]/));
				for(var i = 0; i < numFaces; i++){
					line = ts.ReadLine().split(/[;,]/);
					for(var j = 1; j < line.length; j++)
						faceArrays.push(line[j]);
				}
			}
			if(token[0] == "MeshNormals")
			{
					//Getting Normal Array
				line = ts.ReadLine();
				numNormals = parseInt(line.split(/[^0-9]/));
				for(var i = 0; i < numNormals; i++){
					line = ts.ReadLine().split(/[;,]/);
					for(var j = 0; j < line.length; j++)
						normArrays.push(line[j]);
				}
			}	
			if(token[0] == "MeshTextureCoords")
			{
					//Getting TexCoord Array
				line = ts.ReadLine();
				numUVs = parseInt(line.split(/[^0-9]/));
				for(var i = 0; i < numUVs; i++){
					line = ts.ReadLine().split(/[;,]/);
					for(var j = 0; j < line.length; j++)
						uvArrays.push(line[j]);
				}
			}	
		}
		ts.Close();

			//Write Out Data
		var filepathMT_OUT = filepathMT.replace(/(.x)$/, ".h");
		if(fso.FileExists(filepathMT_OUT))
			logmessage(filepathMT_OUT + " already exists!", siWarning);
		else{
			ts = fso.CreateTextFile( filepathMT_OUT, true );
			ts.Write( "#import \"OpenGLCommon.h\"" + "\n\n" );
			ts.Write( "#define k" + obj3D_Name + "NumberOfVertices " + numVerts +"\n" );
			ts.Write( "#define k" + obj3D_Name + "NumberOfFaces " + numFaces +"\n" );
				
			ts.Write( "\n#pragma mark - Vertex3D" + "\n\n" );
			ts.Write( "static const Vertex3D " + obj3D_Name + "_Vertices[] = {" + "\n" );
			for(var i = 0; i < vertArrays.length; i++){
				vectorWrite(vertArrays[i], 3, i, ts);
			}
			ts.Write("};\n\n");
				
			ts.Write( "\n#pragma mark - Faces Index" + "\n\n" );
			ts.Write( "static const Face3D " + obj3D_Name + "_Faces[] = {" + "\n" );
			for(var i = 0; i < faceArrays.length; i++){
				vectorWrite(faceArrays[i], 3, i, ts);
			}
			ts.Write("};\n\n");
				
			ts.Write( "\n#pragma mark - Normals" + "\n\n" );
			ts.Write( "static const Vector3D " + obj3D_Name + "_Normals[] = {" + "\n" );
			for(var i = 0; i < normArrays.length; i++){
				vectorWrite(normArrays[i], 3, i, ts);
			}
			ts.Write("};\n\n");
			
			ts.Write( "\n#pragma mark - TexCoords" + "\n\n" );
			ts.Write( "static const TextureCoord3D " + obj3D_Name + "_TexCoords[] = {" + "\n" );
			for(var i = 0; i < uvArrays.length; i++){
				vectorWrite(uvArrays[i], 2, i, ts);
			}
			ts.Write("};\n\n");
			ts.Close();
		}

	}

function vectorWrite(value, modulos, iteration, textStream){
	var modSwitch = iteration % modulos;
	if(modSwitch == 0)
		textStream.Write("{");
	textStream.Write(value);
	if(modSwitch != (modulos - 1))
		textStream.Write(", ");
	if(modSwitch == (modulos -1))
		textStream.Write("},\n");
}