import bpy
from Console import log

def deleteSelectedObjects(selected_objects):
    if selected_objects != []:
        for obj in selected_objects:
            wipeOutObject(obj)
            # me = obj.data
            # me.users
            # me.user_clear()
            # bpy.data.meshes.remove(me)

def wipeOutObject(ob,and_data=True) :
    
    data = bpy.data.objects[ob.name].data
    
    # never wipe data before unlink the ex-user object of the scene else crash (2.58 3 770 2) 
    # so if there's more than one user for this data, never wipeOutData. will be done with the last user
    # if in the list
    #if data.users &gt; 1 :
    #    and_data=False
    
    # odd :    
    ob=bpy.data.objects[ob.name]    
    # if the ob (board) argument comes from bpy.data.groups['aGroup'].objects,
    #  bpy.data.groups['board'].objects['board'].users_scene

    bpy.context.collection.objects.unlink(ob)

    try : bpy.data.objects.remove(ob)
    except : print('data.objects.remove issue with %s'%ob.name)
    
    # never wipe data before unlink the ex-user object of the scene else crash (2.58 3 770 2) 
    if(data != None):
        wipeOutData(data)    

def wipeOutData(data) :
    if data.users == 0 :
        try : 
            data.user_clear()
        
            # mesh
            if type(data) == bpy.types.Mesh :
                bpy.data.meshes.remove(data)
            # lamp
            elif type(data) == bpy.types.PointLamp :
                bpy.data.lamps.remove(data)
            # camera
            elif type(data) == bpy.types.Camera :
                bpy.data.cameras.remove(data)
            # Text, Curve
            elif type(data) in [ bpy.types.Curve, bpy.types.TextCurve ] :
                bpy.data.curves.remove(data)
            # metaball
            elif type(data) == bpy.types.MetaBall :
                bpy.data.metaballs.remove(data)
            # lattice
            elif type(data) == bpy.types.Lattice :
                bpy.data.lattices.remove(data)
            # armature
            elif type(data) == bpy.types.Armature :
                bpy.data.armatures.remove(data)
            else :
                print('data still here : forgot %s'%type(data))
                s = ('data still here : forgot %s'%type(data))
                log(s)

        except :
            # empty, field
            print('%s has no user_clear attribute.'%data.name)
    else :
        print('%s has %s user(s) !'%(data.name,data.users))