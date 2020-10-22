from maya import cmds

def getCurvePoints():
    '''Get all the control points in a curve'''
    sel = cmds.ls(sl = True)[0]
    sel_shape = cmds.listRelatives(sel, shapes = True)[0]
    attr_name = 'controlPoints'
    points = cmds.getAttr('{0}.{1}[*]'.format(sel_shape, attr_name))
    
    #returns the points vertically
    for point in points:
        print point
        
    return points

def plus(name = 'plus'):
    '''The shape of a locator'''
    points = [
        (0.0, 1.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, 0.0),
        (-1.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.0, 0.0, -1.0)
        ]
        
    custom_shape = cmds.curve(n = name, p = points, d = 1)

    return custom_shape
    
def cube(name = 'cube'):
    '''The shape of a cube'''
    points = [
    (-1, -1, -1),
    (-1, -1, 1),
    (-1, 1, 1),
    (1, 1, 1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, -1),
    (1, -1, 1),
    (-1, -1, 1),
    (-1, 1, 1),
    (-1, 1, -1),
    (1, 1, -1),
    (1, -1, -1),
    (1, -1, 1),
    (1, 1, 1)
    ]
        
    custom_shape = cmds.curve(n = name, p = points, d = 1)
    
    return custom_shape
    
def poly8(name = 'octahedron'):
    '''The shape of an octahedron, 8-sided polygon'''
    points = [
        (0.0, 0.0, -1.0),
        (-1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, -1.0, 0.0),
        (-1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        (1.0, 0.0, 0.0),
        (0.0, 0.0, -1.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, -1.0)
        ]
    
    custom_shape = cmds.curve(n = name, p = points, d = 1)
    
    return custom_shape