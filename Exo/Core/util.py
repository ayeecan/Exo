from maya import cmds
from contextlib import contextmanager

def getSelected():
    '''List selected objects'''
    selection = cmds.ls(sl = True)
    
    return selection
    
def getUniqueName(name, index = 0):
    '''Make the name unique'''
    validName = name if not index else '{0}{1}'.format(name, index)
    
    if cmds.objExists(validName):
        validName = getUniqueName(name, index = index + 1)
        
    return validName
    
def getCoords(ctrl):
    '''Retrieve translation and rotation of given object'''
    pos = cmds.xform(ctrl, q = True, t = True, ws = True)
    rot = cmds.xform(ctrl, q = True, ro = True, ws = True)
    
    return pos, rot

def listOfPos(list):
    '''Returns a list of positions'''
    coord_list = []
    
    for ctrl in list:
        pos, rot = getCoords(ctrl)
        coord_list.append(pos)
    
    return coord_list    
    
def findParent(node):
    '''Find parent'''
    par_unicode = cmds.listRelatives(node, p = True)
    par = nameReformat(par_unicode)
    
    return par
    
def findShape(node):
    '''Find shape node'''
    shpe_unicode = cmds.listRelatives(node, c = True, shapes = True)
    shpe = nameReformat(shpe_unicode)
    
    return shpe
    
def findFromAttr(node, attr, fromSource):
    '''
    Find a node from another node's attribute from source or destination
    
    VARIABLES:
    node   is a string
    attr   is a string
    source is a boolean
    '''
    found_node_unicode = cmds.listConnections('{0}.{1}'.format(node, attr), d = not fromSource, s = fromSource)
    found_node = nameReformat(found_node_unicode)
    
    return found_node
    
def removeNamespace(ns_name):
    '''Makes namespace as part of the name'''
    new_name = ns_name.replace(':', '_')
        
    return new_name
    
def nameReformat(ctrl):
    """Sometimes names appear as [u'name']. This function converts those names into a useable string"""
    name_reformat = ctrl[0] if type(ctrl) == list else ctrl

    return name_reformat
    
def listToString(list):
    '''Makes a list into a string'''
    newString = ''
    for i, item in enumerate(list):
        if i == 0:
            newString += item
        else:
            newString += ',{0}'.format(item)
            
    return newString
    
def setPrefix(name, prefix = 'exo_'):
    '''Add prefix to each name'''
    new_name = prefix + name
        
    return new_name

def niceName(ctrl, prefix = 'exo_'):
    '''Returns a name with a prefix and no namespace'''
    ns_name = removeNamespace(ctrl)
    new_name = setPrefix(ns_name, prefix)
        
    return new_name
    
def listOfNames(list, prefix):
    '''Returns a new list of names'''
    name_list = []
    
    for ctrl in list:
        new_name = niceName(ctrl, prefix)
        name_list.append(new_name)
        
    return name_list
    
def snap(obj_child, obj_parent):
    '''Match transformations of child to parent'''
    with tempUnlockCB(obj_child):
        cmds.matchTransform(obj_child, obj_parent)

def parentWithLocks(obj_child, obj_parent):
    '''Put children under hierarchy of parent'''
    with tempUnlockCB(obj_child):
        cmds.parent(obj_child, obj_parent)
    
def parentUnderHierarchy(obj_child, obj_parent):
    '''Put the parent node back in its hierarchy after running parentWithLocks'''
    ctrl_parent = cmds.listRelatives(obj_child, parent = True)
    
    parentWithLocks(obj_child, obj_parent)
    if ctrl_parent is not None:
        parentWithLocks(obj_parent, ctrl_parent[0])
    
def cons(master, slave):
    '''Constrain slave to master. Master will match transforms of slave.'''
    snap(master, slave)
    cons_node = cmds.parentConstraint(master, slave)
    
    return cons_node

@contextmanager
def saveTime():
    '''set time to 1 and then set it back to whatever the time was'''
    curTime = cmds.currentTime(q = True)
    cmds.currentTime(1, e = True)
    yield
    cmds.currentTime(curTime, e = True)
    
@contextmanager
def tempUnlockCB(ctrl):
    '''Temporarily unlock translate, rotate, and scale from the channel box'''
    attr_list = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    child_cbAttrs = cbAttrs(ctrl)
    locked = checkForLocks(ctrl, attr_list)
    
    if locked: unlockCB(ctrl, unlock_list = attr_list)
    yield
    if locked: lockCB(ctrl, custom_lock = attr_list)
    if child_cbAttrs is not None:
        unlockCB(ctrl, unlock_list = child_cbAttrs)
    
def checkForLocks(ctrl, attrToCheck):
    '''Check if any of the attributes are locked'''
    ctrl_name = nameReformat(ctrl)
    
    for atr in attrToCheck:
        lock_result = cmds.getAttr('{0}.{1}'.format(ctrl_name, atr), lock = True)
        if lock_result:
            return True
    
    return False
    
def cbAttrs(ctrl):
    '''Find all visible attributes in the channel box'''
    cb_list = cmds.listAnimatable(ctrl)
    new_list = []
    
    if cb_list is not None:
        for atr_long in cb_list:
            atr_short = atr_long.rpartition('.')[2]
            new_list.append(atr_short)
        
        return new_list
    
    return
    
def lockCB(ctrl, lockDefault = False, lockArnold = False, custom_lock = [], use_shape = False):
    '''
    Locks and hides attributes from the Channel Box
    
    Will lock only one list (default, arnold, custom)
    If multiple locks are needed run this function again for each lock
    lockArnold will automatically toggle use_shape to True
    '''
    ai_lock_list = ['aiRenderCurve', 'aiCurveWidth', 'aiSampleRate', 'aiCurveShaderR', 'aiCurveShaderG', 'aiCurveShaderB']
    default_lock_list = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
    selList = []
    ctrl_name = nameReformat(ctrl)

    if lockDefault:
        selList = default_lock_list
    elif lockArnold:
        if cmds.pluginInfo('mtoa.mll', q = True, loaded = True):
            selList = ai_lock_list
            use_shape = True
        else:
            return
    else:
        selList = custom_lock
    
    attr_node = findShape(ctrl_name) if use_shape else ctrl_name
    
    for one_attr in selList:
        cmds.setAttr('{0}.{1}'.format(attr_node, one_attr),
                     lock       = True,
                     keyable    = False,
                     channelBox = False
                    )
                    
def unlockCB(ctrl, unlock_list = []):
    '''Unlocks attributes in list'''
    ctrl_name = nameReformat(ctrl)
    
    for one_attr in unlock_list:
        cmds.setAttr('{0}.{1}'.format(ctrl_name, one_attr),
                     lock       = False,
                     keyable    = True
                    )
        