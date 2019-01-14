from maya import cmds, mel

from Exo.Core import util

reload(util)

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
    
def brandJiggle(master_node, selectedCtrls):
    '''An attribute to store selected controls for a jiggle'''
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
    
def ctrlLock(ctrl):
    '''Lock and brand the control'''
    branding(ctrl, 'exo_control')
    util.lockCB(ctrl, lockArnold = True)
    lock_list = ['sx', 'sy', 'sz', 'v']
    util.lockCB(ctrl, custom_lock = lock_list)
    
    return ctrl
    
def pivot(name):
    '''Make a pivot control'''
    points = [(0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]
    new_name = '{0}_pivot'.format(name)
    
    pivot_node = cmds.curve(n = new_name, p = points, d = 1)
    
    ctrlLock(pivot_node)
    
    return pivot_node
    
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

def splineIK(name, startJnt, endJnt, curve):
    '''
    Create an ik spline
    Returns both the handle and effector
    '''
    handle, eff = cmds.ikHandle(n = '{0}_ikH'.format(name), startJoint = startJnt, endEffector = endJnt, curve = curve,
                           sol = 'ikSplineSolver', ccv = False, roc = False, pcv = False, snc = True)
                           
    eff_rename = cmds.rename(eff, '{0}_eff'.format(name))
    
    return handle, eff_rename
    
def buildCtrl():
    #selection of objects
    master_ctrl = 'exo_master'
    dummy_text = 'dummy'
    
    new_name = util.getUniqueName(util.setPrefix(dummy_text))
        
    #submaster control
    submaster_ctrl = null('{0}_master'.format(new_name), new_name, 'control', master = True)
    util.parentWithLocks(submaster_ctrl, master_ctrl)
    
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
        
    cmds.select(clear = True)
    
def buildJiggle():
    with util.saveTime():
        all_sel = util.getSelected()
        if len(all_sel) < 2:
            cmds.warning('Not enough controls selected')
            return
        
        #a list of nice names and translations
        name_list = util.listOfNames(all_sel, 'jiggle_')
        coord_list = util.listOfPos(all_sel)
        naming_standard = name_list[0]

        #make the joints
        jnt_list = jointChain(name_list, coord_list)
        
        #constrain the controls to their respective joints
        for i, jnt in enumerate(jnt_list):
            cmds.orientConstraint(jnt, all_sel[i], mo = True)
        
        #make a dynamic curve
        source_curve = cmds.curve(n = '{0}_sourceCurve'.format(naming_standard), ep = coord_list)
        cmds.setAttr('{0}.visibility'.format(source_curve), 0)
        fol_node, fol_grp, dyn_curve, dyn_grp, hair_node, nuc_node = makeCurveDynamic(source_curve, naming_standard)
            
        #ik spline the dynamic curve
        handle, eff = splineIK(naming_standard, jnt_list[0], jnt_list[-1], dyn_curve)
        
        #make a new group for joints and dyn_grp
        move_grp = cmds.group(n = '{0}_moveGrp'.format(naming_standard), empty = True)
        cmds.parent(fol_grp, jnt_list[0], move_grp)
        cmds.pointConstraint(all_sel[0], move_grp, mo = True)
        
        list_for_master = [hair_node, nuc_node, handle, move_grp, dyn_grp]
        submaster_ctrl = null('{0}_master'.format(naming_standard), naming_standard, 'jiggle', master = True)
        brandJiggle(submaster_ctrl, all_sel)
        cmds.parent(list_for_master, submaster_ctrl)
        
        master_ctrl = 'exo_master'
        cmds.parent(submaster_ctrl, master_ctrl)
        
        cmds.select(clear = True)        
    