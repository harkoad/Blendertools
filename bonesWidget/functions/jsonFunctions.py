import bpy
import os
import json

def objectDataToDico(object) :
    verts = []
    for v in object.data.vertices:
        verts.append(v.co.to_tuple())

    polygons = []
    for p in object.data.polygons:
        polygons.append(tuple(p.vertices))
    
    edges = []
    
    for e in object.data.edges:
        if len(polygons)!= 0 :
            for vert_indices in polygons :                         
                if e.key[0] and e.key[1] not in vert_indices :
                    edges.append(e.key)
        else :
            edges.append(e.key)
                
    wgts = {"vertices":verts,"edges":edges,"faces":polygons}    
    print(wgts)
    return(wgts)

def readWidgets():
    wgts = {}
    
    jsonFile = os.path.join(os.path.dirname(os.path.dirname(__file__)),'widgets.json')
    if os.path.exists(jsonFile):
        f = open(jsonFile,'r')
        wgts = json.load(f)

    return (wgts)

def addRemoveWidgets(context,addOrRemove,items,widgets):
    wgts = readWidgets()
        
    widget_items=[]
    for widget_item in items :
        widget_items.append(widget_item[1])
    
    if addOrRemove == 'add' :        
        for ob in widgets :        
            ob_name = ob.name.replace("WGT-","")
            wgts[ob_name]= objectDataToDico(ob)
            if (ob_name,ob_name,"") not in widget_items :
                widget_items.append(ob_name)      
        
    elif addOrRemove == 'remove' :
        del wgts[widgets]           
        widget_items.remove(widgets)

    del bpy.types.Scene.widget_list
    
    widget_itemsSorted = []
    for w in sorted(widget_items) :
        widget_itemsSorted.append((w,w,""))
    
    bpy.types.Scene.widget_list = bpy.props.EnumProperty(items=widget_itemsSorted)                
            
    jsonFile = os.path.join(os.path.dirname(os.path.dirname(__file__)),'widgets.json')
    if os.path.exists(jsonFile):
        f = open(jsonFile,'w')
        f.write(json.dumps(wgts))
        f.close()

