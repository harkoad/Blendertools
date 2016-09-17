import bpy

from .functions import symmetrizeShape
from .functions import fromWidgetFindBone
from .functions import createWidget
from .functions import editWidget
from .functions import returnToArmature
from .functions import addRemoveWidgets
from .functions import readWidgets
from bpy.types import Operator  
from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty


class bw_createWidget(bpy.types.Operator):
    bl_idname = "bonewidget.create_widget"
    bl_label = "Create"
    bl_options = {'REGISTER', 'UNDO'}  

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.mode == 'POSE')

    global_size = FloatProperty(  
       name="Global Size :",  
       default=1.0,  
       description="Global Size :" 
       )  

    scale = FloatVectorProperty(  
       name="Scale :",  
       default=[1,1,1],  
       description="Scale :" 
       )  

    slide = FloatProperty(  
       name="Slide :",  
       default=0.0,  
       subtype='DISTANCE',  
       unit='LENGTH',  
       description="slide"  
       ) 

    def execute(self, context):       
        wgts = readWidgets()
        for bone in bpy.context.selected_pose_bones :
            createWidget(bone,wgts[context.scene.widget_list],self.global_size,self.scale,self.slide,1)
    
        return {'FINISHED'}


class bw_editWidget(bpy.types.Operator):
    bl_idname = "bonewidget.edit_widget"
    bl_label = "Edit"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.pose)

    def execute(self, context):
        editWidget(context.active_pose_bone)
        return {'FINISHED'}


class bw_returnToArmature(bpy.types.Operator):
    bl_idname = "bonewidget.return_to_armature"
    bl_label = "Return to armature"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH' 
            and context.object.mode == 'EDIT' 
                or context.object.mode == 'OBJECT')

    def execute(self, context):
        if fromWidgetFindBone(bpy.context.object):    
            returnToArmature(bpy.context.object)
        
        else :
            self.report({'INFO'}, 'Object is not a bone widget')
        
        return {'FINISHED'}

class bw_MatchBoneTransforms(bpy.types.Operator):
    bl_idname = "bonewidget.match_bone_transforms"
    bl_label = "Match bone transforms"

    def execute(self, context):
        widgets = []
        if bpy.context.object.type== "ARMATURE" :
            for bone in bpy.context.selected_pose_bones :
                widgets.append(bone.custom_shape)
            
        else :
            widgets = bpy.context.selected_objects
                
        for widget in widgets : 
            matchBone = fromWidgetFindBone(widget)
            if matchBone :
                widget.matrix_local = matchBone.bone.matrix_local
                widget.scale = [matchBone.bone.length,matchBone.bone.length,matchBone.bone.length]
                widget.data.update()
        return {'FINISHED'}


class bw_match_symmetrizeShape(bpy.types.Operator):
    bl_idname = "bonewidget.symmetrize_shape"
    bl_label = "Symmetrize"
    bl_options = {'REGISTER', 'UNDO'}  
       
    def execute(self, context):
        symmetrizeShape()
        return {'FINISHED'}


class bw_addWidgets(bpy.types.Operator):
    bl_idname = "bonewidget.add_widgets"
    bl_label = "Add Widgets"

    def execute(self, context):
        objects=[]
        if bpy.context.mode == "POSE" :
            for bone in bpy.context.selected_pose_bones :
                objects.append(bone.custom_shape)
        else  :
            for ob in bpy.context.selected_objects :
                if ob.type == 'MESH' :
                    objects.append(ob)
        
        if not objects :
            self.report({'INFO'}, 'Select Meshes or Pose_bones')
            
        addRemoveWidgets(context,"add",bpy.types.Scene.widget_list[1]['items'],objects)
    
        return {'FINISHED'}

class bw_removeWidgets(bpy.types.Operator):
    bl_idname = "bonewidget.remove_widgets"
    bl_label = "Remove Widgets"

    def execute(self, context):
        objects= bpy.context.scene.widget_list
        addRemoveWidgets(context,"remove",bpy.types.Scene.widget_list[1]['items'],objects)
        return {'FINISHED'}