import bpy
import numpy
from .jsonFunctions import objectDataToDico

def fromWidgetFindBone(widget):
    matchBone = None
    for ob in bpy.context.scene.objects :
        if ob.type == "ARMATURE" : 
            for bone in ob.pose.bones :
                if bone.custom_shape == widget:
                    matchBone = bone
                    
    return matchBone

def createWidget(bone,widget,size,scale,slide,invert):
    C = bpy.context
    D = bpy.data

    if bone.custom_shape :
        bone.custom_shape.name = bone.custom_shape.name+"_old"
        bone.custom_shape.data.name = bone.custom_shape.data.name+"_old"
        if [True for i in C.scene.objects if bone.custom_shape == i] :
            C.scene.objects.unlink(bone.custom_shape)
        
    newData = D.meshes.new(bone.name)
    print(widget['faces'])
    newData.from_pydata(numpy.array(widget['vertices'])*[size*invert*scale[0],size*scale[2],size*scale[1]]+[0,slide,0],widget['edges'],widget['faces'])
    newData.update(calc_edges=True)
    if invert == 1 :
        newObject = D.objects.new('WGT-%s'%bone.name,newData)    

    else :
        newObject = findMirrorObject(bone).custom_shape.copy()

    newObject.data = newData
    newObject.name = 'WGT-%s'%bone.name
    C.scene.objects.link(newObject)
    newObject.matrix_local = bone.bone.matrix_local
    newObject.scale = [bone.bone.length,bone.bone.length,bone.bone.length]

    newData.update()
    bone.custom_shape = newObject
    bone.bone.show_wire = True
    newObject.layers = [False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False]
        
def editWidget(active_bone):
    C = bpy.context
    D = bpy.data
    widget = active_bone.custom_shape
    
    armature = active_bone.id_data
    bpy.ops.object.mode_set(mode='OBJECT')
    C.active_object.select = False
    visibleLayers = numpy.array(bpy.context.scene.layers)+widget.layers-armature.layers

    bpy.context.scene.layers = visibleLayers.tolist()    
    
    if C.space_data.local_view :
        bpy.ops.view3d.localview()
    
    bpy.context.scene.objects.active = widget      
    bpy.ops.object.mode_set(mode='EDIT')
      
def returnToArmature(widget):
    C = bpy.context
    D = bpy.data
          
    bone = fromWidgetFindBone(widget)
    armature = bone.id_data
    
    if C.active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    visibleLayers = numpy.array(bpy.context.scene.layers)-widget.layers+armature.layers
    bpy.context.scene.layers = visibleLayers.tolist()
    
    
    if C.space_data.local_view :
        bpy.ops.view3d.localview()
    bpy.context.scene.objects.active = armature
    armature.select = True
    bpy.ops.object.mode_set(mode='POSE')
    armature.data.bones[bone.name].select = True
    armature.data.bones.active = armature.data.bones[bone.name]
            

def findMirrorObject(object):
    if object.name.endswith("L") :
        suffixe = 'R'
    elif object.name.endswith("R") :
        suffixe = 'L'

    objectName = list(object.name)
    objectBaseName = objectName[:-1]
    mirroredObjectName = "".join(objectBaseName)+suffixe
    
    if object.id_data.type == 'ARMATURE' :
        return object.id_data.pose.bones.get(mirroredObjectName)
    else :
        return bpy.context.scene.objects.get(mirroredObjectName)
    
def symmetrizeShape():
    C = bpy.context
    D = bpy.data
    
    widgetsAndBones = {}
    
    if bpy.context.object.type == 'ARMATURE':
        for bone in C.selected_pose_bones : 
            if bone.name.endswith("L") or bone.name.endswith("R"):
                widgetsAndBones[bone] = bone.custom_shape            
                mirrorBone = findMirrorObject(bone)
                if mirrorBone :
                    widgetsAndBones[mirrorBone]= mirrorBone.custom_shape 
        
        armature = bpy.context.object
        activeObject = C.active_pose_bone
    else :
        for shape in C.selected_objects : 
            bone = fromWidgetFindBone(shape)
            if bone.name.endswith("L") or bone.name.endswith("R"):
                widgetsAndBones[fromWidgetFindBone(shape)] = shape
            
                mirrorShape = findMirrorObject(shape)
                if mirrorShape :
                   widgetsAndBones[mirrorShape]= mirrorShape
        
        activeObject = fromWidgetFindBone(C.object)
        armature = activeObject.id_data
    
    for bone in widgetsAndBones :
        if activeObject.name.endswith("L") :
            if bone.name.endswith("L") and widgetsAndBones[bone]:
                createWidget(findMirrorObject(bone),objectDataToDico(widgetsAndBones[bone]),1,[1,1,1],0,-1)
        else :
            if bone.name.endswith("R") and widgetsAndBones[bone]:
                createWidget(findMirrorObject(bone),objectDataToDico(widgetsAndBones[bone]),1,[1,1,1],0,-1)
    