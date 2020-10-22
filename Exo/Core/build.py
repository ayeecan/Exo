from maya import cmds, mel, OpenMaya

from Exo.Core import util, shapes

reload(util)
reload(shapes)

def branding(ctrl, brand_label, brand_text = ''):
    '''Adds an attribute to a control to identify it as an Exo control'''
    ctrl_name = util.nameReformat(ctrl)
    attr_name = '{0}.{1}'.format(ctrl_name, brand_label)
    
    cmds.addAttr(ctrl, ln=brand_label, dt='string')
    if brand_text:
        cmds.setAttr(attr_name, brand_text, type = 'string')
    cmds.setAttr(attr_name, lock = True)
    
    newAttr_name = '{0}.{1}'.format(ctrl_name, brand_label)
    return newAttr_name
    
def storeCtrls(master_node, selectedCtrls):
    '''An attribute under the submaster control to store selected controls '''
    attr_label = 'controls_used'
    fullName = '{0}.{1}'.format(master_node, attr_label)
    
    cmds.addAttr(master_node, ln = attr_label, dt = 'stringArray')
    selCtrl_str = util.listToString(selectedCtrls)
    cmds.setAttr(fullName, len(selectedCtrls), type = 'stringArray', *selectedCtrls)
    cmds.setAttr(fullName, lock = True)
    
    return fullName
    
def brandMasterID(ctrl, exo_name, exo_type):
    '''Add attributes for the UI to properly categorize the node'''
    branding(ctrl, 'exo_control')
    branding(ctrl, 'exo_name', exo_name)
    branding(ctrl, 'exo_type', exo_type)
    
def null(name, exo_name = '', exo_type = '', master = False):
    '''Make an empty group'''
    null_node = cmds.group(n = name, empty = True)
    
    if master:
        brandMasterID(null_node, exo_name, exo_type)
    else:
        branding(null_node, 'exo_control')
    util.lockCB(null_node, lockDefault = True)
    
    return null_node
    
def nullify(ctrl):
    """Make an empty group to nullify an object's attributes"""
    ctrl_name = util.nameReformat(ctrl)
    null_name = '{0}_null'.format(ctrl_name)
    null_node = null(null_name)
    
    util.snap(null_node, ctrl_name)
    util.parentUnderHierarchy(ctrl_name, null_node)
        
    return null_node
    
def ctrl(name, offset = False):
    '''Make an Exo control'''
    if offset:
        new_name = '{0}_offset'.format(name)
        set_rad = 1.0
    else:
        new_name = name
        set_rad = 1.5
    
    ctrl_node = cmds.circle(n = new_name, r = set_rad, nr = (0,1,0), sw = 360, ch = False)
    
    ctrlLock(ctrl_node)
    
    return ctrl_node
    
def ctrl_ik(name):
    '''Make a control for an ik handle'''
    new_name = '{0}_ikCtrl'.format(name)
    
    ik_node = shapes.cube(new_name)
    ctrlLock(ik_node)
    
    return ik_node
    
def pivot(name):
    '''Make a pivot control'''
    new_name = '{0}_pivot'.format(name)
    
    pivot_node = shapes.plus(new_name)
    ctrlLock(pivot_node)
    
    return pivot_node
    
def ctrlLock(ctrl):
    '''Lock and brand the control'''
    branding(ctrl, 'exo_control')
    util.lockCB(ctrl, lockArnold = True)
    lock_list = ['sx', 'sy', 'sz', 'v']
    util.lockCB(ctrl, custom_lock = lock_list)
    
    return ctrl
    
def negative(name):
    '''Create a node that makes translation negative'''
    new_name = '{0}_neg'.format(name)
    neg_node = cmds.shadingNode('multiplyDivide', asUtility = True, n = new_name)
    
    cmds.setAttr('{0}.input2X'.format(neg_node), -1)
    cmds.setAttr('{0}.input2Y'.format(neg_node), -1)
    cmds.setAttr('{0}.input2Z'.format(neg_node), -1)
    
    return neg_node
    
def jointChain(names, positions):
    '''Create a joint chain'''
    #clear selection so joints don't get parented under a control
    cmds.select(clear = True)
    
    jnt_list = []
    for i, coord in enumerate(positions):
        jnt = cmds.joint(n = '{0}_jnt'.format(names[i]), p = coord)
        jnt_list.append(jnt)
        
    cmds.joint(jnt_list, e = True, zso = True, oj = 'xyz', sao = 'yup')
    
    return jnt_list
    
def constrainSelectedToJoints(names, positions, selection):
    '''Create a joint chain and constrain selected controls to each respectful joint'''
    jnt_list = jointChain(names, positions)
    for i, jnt in enumerate(jnt_list):
        cmds.orientConstraint(jnt, selection[i], mo = True)
        
    return jnt_list
        
def makeCurveDynamic(curve, name):
    '''
    Run nHair makeCurvesDynamic function and locate all the nodes it creates
    
    Returns the following nodes in order:
    Follicle, Follicle Group, Out Curve, Out Curve Group, Hair System, Nucleus
    '''
    cmds.select(curve, r = True)
    #this makes the curve dynamic
    mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')
    
    #the rest identifies all nodes made from the mel function and renames them
    fol_node   = util.findParent(curve)
    fol_shape  = util.findShape(fol_node)
    #take the follicle's shape node and set point lock to 1(which is to hold the curve at its Base)
    cmds.setAttr('{0}.pointLock'.format(fol_shape), 1)
    fol_grp    = util.findParent(fol_node)
    
    dyn_curve  = util.findFromAttr(fol_shape, 'outCurve', fromSource = False)
    dyn_grp    = util.findParent(dyn_curve)
    
    hair_node  = util.findFromAttr(fol_shape, 'currentPosition', fromSource = True)
    hair_shape = util.findShape(hair_node)
    
    nuc_node   = util.findFromAttr(hair_shape, 'startFrame', fromSource = True)
    
    newName_fol      = cmds.rename(fol_node,  '{0}_fol'.format(name))
    newName_folgrp   = cmds.rename(fol_grp,   '{0}_fol_grp'.format(name))
    newName_curve    = cmds.rename(dyn_curve, '{0}_dynCurve'.format(name))
    newName_curvegrp = cmds.rename(dyn_grp,   '{0}_dynCurve_grp'.format(name))
    newName_hair     = cmds.rename(hair_node, '{0}_hair'.format(name))
    newName_nuc      = cmds.rename(nuc_node,  '{0}_nuc'.format(name))
    
    
    return newName_fol, newName_folgrp, newName_curve, newName_curvegrp, newName_hair, newName_nuc

def makeIK(name, jntList, solve_type, curve = None):
    '''
    Create an ik chain. The type of ik must be specified in the solve_type variable
    Returns both the handle and effector
    '''
    startJnt = jntList[0]
    endJnt = jntList[-1]
    
    if curve is None:
        handle, eff = cmds.ikHandle(n = '{0}_ikHandle'.format(name), startJoint = startJnt, endEffector = endJnt, sol = solve_type)
    else:
        handle, eff = cmds.ikHandle(n = '{0}_ikHandle'.format(name), startJoint = startJnt, endEffector = endJnt, curve = curve,
                                    sol = solve_type, ccv = False, roc = False, pcv = False, snc = True)
                           
    eff_rename = cmds.rename(eff, '{0}_eff'.format(name))
    
    if solve_type == 'ikRPsolver':
        pv_node = makePV(name, jntList, handle)
        return handle, eff_rename, pv_node
    else:
        return handle, eff_rename

def makePV(name, jntList, handle):
    '''Create a pole vector'''
    new_name = '{0}_pv'.format(name)
    pv_node = shapes.poly8(new_name)
    ctrlLock(pv_node)
    lock_list = ['rx', 'ry', 'rz']
    util.lockCB(pv_node, custom_lock = lock_list)
    
    
    startCoord = util.getCoords(jntList[0])[0]
    midCoord   = util.getCoords(jntList[1])[0]
    endCoord   = util.getCoords(jntList[2])[0]
    posX, posY, posZ = pvMath(startCoord, midCoord, endCoord)
    cmds.move(posX, posY, posZ, pv_node)
    
    cmds.poleVectorConstraint(pv_node, handle)
    
    return pv_node
    
def pvMath(start, mid, end):
    '''
    Finds where the pole vector should be.
    Taken from Marco Giordano: https://vimeo.com/66015036
    
    pv_distance: how far from the joints should the pole vector be
    Returns x y z coords individually
    '''
    pv_distance = 1
    
    startV = OpenMaya.MVector(start[0], start[1], start[2])
    midV   = OpenMaya.MVector(mid[0] ,  mid[1],   mid[2])
    endV   = OpenMaya.MVector(end[0] ,  end[1],   end[2])

    startEnd = endV - startV
    startMid = midV - startV

    dotP = startMid * startEnd
    proj = float(dotP) / float(startEnd.length())
    startEndN = startEnd.normal()
    projV = startEndN * proj

    arrowV = startMid - projV
    arrowV*= pv_distance
    finalV = arrowV + midV
    
    return finalV.x, finalV.y, finalV.z

def createMaster():
    '''Create a master Exo node if there is none'''
    master_name = 'exo_master'
    if not cmds.objExists(master_name):
        null(master_name)
        
    cmds.select(clear = True)
        
    return master_name
    
def buildCtrl():
    cur_sel = cmds.ls(sl = True)
    #selection of objects
    master_ctrl = createMaster()
    dummy_text = 'dummy'
    
    new_name = util.getUniqueName(util.setPrefix(dummy_text))
        
    #submaster control
    submaster_ctrl = null('{0}_master'.format(new_name), new_name, 'control', master = True)
    util.parentWithLocks(submaster_ctrl, master_ctrl)
    
    #actual controller
    new_ctrl = ctrl(new_name)
    util.parentUnderHierarchy(new_ctrl, submaster_ctrl)
    util.unlockCB(new_ctrl, ['sx', 'sy', 'sz'])
    
    new_pivot = pivot(new_name)
    util.parentUnderHierarchy(new_pivot, new_ctrl)
    
    new_neg_offset = null('{0}_neg_offset'.format(new_name))
    util.parentUnderHierarchy(new_neg_offset, new_pivot)
    
    neg_node = negative(new_name)
    cmds.connectAttr('{0}.translate'.format(new_pivot), '{0}.input1'.format(neg_node))
    with util.tempUnlockCB(new_neg_offset):
        cmds.connectAttr('{0}.output'.format(neg_node), '{0}.translate'.format(new_neg_offset))
    
    new_offset = ctrl(new_name, offset = True)
    util.parentUnderHierarchy(new_offset, new_neg_offset)
        
    if cur_sel != []:
        cmds.matchTransform(new_ctrl, cur_sel)
        util.autoSize(new_ctrl, cur_sel)
        
    cmds.select(clear = True)
    
def buildJiggle():
    jiggle_text = 'jiggle'
    solver_text = 'ikSplineSolver'
    with util.saveTime():
        all_sel = cmds.ls(sl = True)
        if len(all_sel) < 2:
            cmds.warning('Not enough controls selected')
            return
        
        name_list, coord_list, naming_standard = util.getNamesPos(all_sel, '{0}_'.format(jiggle_text))

        jnt_list = constrainSelectedToJoints(name_list, coord_list, all_sel)
        
        #make a dynamic curve
        source_curve = cmds.curve(n = '{0}_sourceCurve'.format(naming_standard), ep = coord_list)
        cmds.setAttr('{0}.visibility'.format(source_curve), 0)
        fol_node, fol_grp, dyn_curve, dyn_grp, hair_node, nuc_node = makeCurveDynamic(source_curve, naming_standard)
            
        #ik spline the dynamic curve
        handle, eff = makeIK(naming_standard, jnt_list, solver_text, dyn_curve)
        
        #make a new group for joints and dyn_grp
        move_grp = cmds.group(n = '{0}_moveGrp'.format(naming_standard), empty = True)
        cmds.parent(fol_grp, jnt_list[0], move_grp)
        cmds.pointConstraint(all_sel[0], move_grp, mo = True)
        
        list_for_master = [hair_node, nuc_node, handle, move_grp, dyn_grp]
        #submaster
        submaster_ctrl = null('{0}_master'.format(naming_standard), naming_standard, jiggle_text, master = True)
        storeCtrls(submaster_ctrl, all_sel)
        cmds.parent(list_for_master, submaster_ctrl)
        
        master_ctrl = createMaster()
        cmds.parent(submaster_ctrl, master_ctrl)
        
        cmds.select(clear = True)        
    
def buildIK():
    ik_text = 'ik'
    solver_text = 'ikRPsolver'
    
    all_sel = cmds.ls(sl = True)    
    if len(all_sel) < 3:
        cmds.warning('Please select 3 controls')
        return
        
    name_list, coord_list, naming_standard = util.getNamesPos(all_sel, '{0}_'.format(ik_text))
    
    jnt_list = constrainSelectedToJoints(name_list, coord_list, all_sel)
    jnt_start = jnt_list[0]
    #the first joint will follow the position of the first selected control(to act as a parent relationship)
    #but the selected controls will follow the rotation of the joints
    cmds.pointConstraint(all_sel[0], jnt_start)
    #make joints invisible
    cmds.setAttr('{0}.visibility'.format(jnt_start), 0)
    
    handle, eff, pv_node = makeIK(naming_standard, jnt_list, solver_text)
    #make handle invisible
    cmds.setAttr('{0}.visibility'.format(handle), 0)
    
    handle_ctrl = ctrl_ik(naming_standard)
    util.cons(handle_ctrl, handle)
    
    list_for_master = [pv_node, handle_ctrl, jnt_start, handle]
    #submaster
    submaster_ctrl = null('{0}_master'.format(naming_standard), naming_standard, ik_text, master = True)
    storeCtrls(submaster_ctrl, all_sel)
    cmds.parent(list_for_master, submaster_ctrl)
    
    master_ctrl = createMaster()
    cmds.parent(submaster_ctrl, master_ctrl)
    
    cmds.select(clear = True)
    