#!/usr/bin/python3

import sys
import copy
import math

class units_base:
# convert 2.54mm steps (1/10 inch) into PCB unit
# legacy is mil then unit=100
# new format is 1/10 mil then unit=1000
    def __init__(self, val ):
        self.unit = val

class XY_base(units_base):
    def __init__( self , val , unit , isCopy = 0 ):
        if isCopy == 1:
            super( XY_base, self).__init__( val.unit )
            self.center_x = val.center_x
            self.center_y = val.center_y
        else:
            super( XY_base, self).__init__( unit )
            self.center_x = val[ 0 ]
            self.center_y = val[ 1 ]

class Widths(units_base):
    def __init__(self, val):
        super( Widths, self).__init__( 100 )
        self.w = val
    def export2string(self):
        return str(int(round(self.w*self.unit)))

class XY(XY_base):
    def __init__( self, xy_val , offset ):
        super( XY, self).__init__( offset , 0 , 1 )
        self.x = xy_val[ 0 ]
        self.y = xy_val[ 1 ]
    def export2string(self):
        return str(int(round((self.x + self.center_x)*self.unit))) + ' ' + str(int(round(( -self.y + self.center_y)*self.unit)))
    def importFromArray(self, xy_val):
        self.x = xy_val[ 0 ]
        self.y = xy_val[ 1 ]
# Not functions to generat'e the 4 quadrants has been designed as
# the combintion of the central symetry with some other do the job
# Indeed, all the combinaisons of 2 orthogonal symetries has a central symetry 
    def symetries_diagonal( self ):
        self.x, self.y = self.y, self.x
    def symetries_x_axis( self ):
        self.y = -self.y
    def symetries_central( self ):
        self.x = -self.x
        self.y = -self.y

class XY1XY2(XY):
    def __init__( self, xy_val , offset ):
        self.left = XY( xy_val , offset )
        self.right = XY( xy_val , offset )
    def next_point( self, xy_val , offset ):
        self.left = self.right
        self.right = XY( xy_val , offset )
    def export2string( self):
        return self.left.export2string() + ' ' + self.right.export2string()


class XY_list:
    def __init__( self, xy_list , offset ):
        self.elementPoint = []
        for i,val in enumerate( xy_list ):
            self.elementPoint.append( XY( val , offset) )
                
# The following functions append the symetric of each element
# The final size of the list is multiplied by 2
    def symetries_diagonal( self ):
        f1 = []
        for i,val in enumerate( self.elementPoint ):
            f2 = copy.deepcopy( val )
            f2.symetries_diagonal()
            f1.append( f2 )
        self.elementPoint += f1
    def symetries_x_axis( self ):
        f1 = []
        for i,val in enumerate( self.elementPoint ):
            f2 = copy.deepcopy( val )
            f2.symetries_x_axis()
            f1.append( f2 )
        self.elementPoint += f1
    def symetries_central( self ):
        f1 = []
        for i,val in enumerate( self.elementPoint ):
            f2 = copy.deepcopy( val )
            f2.symetries_central()
            f1.append( f2 )
        self.elementPoint += f1

class XY1XY2_list:
    def __init__( self, xy_list , offset ):
        for i,val in enumerate( xy_list ):
            if i == 0:
                self.f1 = XY1XY2( val , offset)
                self.elementPoint = []
            else:
                self.f1.next_point( val , offset )
                self.elementPoint.append( copy.deepcopy( self.f1 ))
# The following functions append the symetric of each element
# The final size of the list is multiplied by 2
    def symetries_diagonal( self ):
        f1 = []
        for i,val in enumerate( self.elementPoint ):
            f2 = copy.deepcopy( val )
            f2.left.symetries_diagonal()
            f2.right.symetries_diagonal()
            f1.append( f2 )
        self.elementPoint += f1
    def symetries_x_axis( self ):
        f1 = []
        for i,val in enumerate( self.elementPoint ):
            f2 = copy.deepcopy( val )
            f2.left.symetries_x_axis()
            f2.right.symetries_x_axis()
            f1.append( f2 )
        self.elementPoint += f1
    def symetries_central( self ):
        f1 = []
        for i,val in enumerate( self.elementPoint ):
            f2 = copy.deepcopy( val )
            f2.left.symetries_central()
            f2.right.symetries_central()
            f1.append( f2 )
        self.elementPoint += f1



o1 = "0x01"

def write_pin( of, posit, ring, drill, num, opts ):
    of.write('\tPin(' + posit.export2string() + ' ' + ring.export2string() + ' ' + drill.export2string() + ' "' + str( num ) + '" ' + ' "' + str( num ) + '" ' + opts + ')\n' )
def write_elements_list( of, xy_list , width ):
    for i,val in enumerate( xy_list.elementPoint ):
        of.write('\tElementLine(' + val.export2string() + ' ' + width.export2string() + ')\n' )


# List of group of silk elements
# each group has a width, a type L=line, a symtries code, a list of points
element_RM5_D_core = [[ 0.09 , 'L' , 'Diags' , [[ -1.1, 1.1 ],[ 0.0, 2.5 ],[ 1.5, 2.5],[ 1.8, 2.2]]]]
element_RM6_D_core = [[ 0.09 , 'L' , 'Diags' , [[ -1.20, 1.20 ],[ 0.0, 3.0 ],[ 2.0, 3.0 ],[ 2.25, 2.75 ]]]]
element_RM6_T_core = [[ 0.09 , 'L' , 'XY' , [[ -1.6, 0 ],[ -2, 2 ],[ -0.75, 3.50 ],[ -0.5, 3.5 ]]]]
element_RM8_D_core = [[ 0.09 , 'L' , 'Diags' , [[ -1.5, 1.5],[ -0.5, 2.5],[ -0.3, 4.0 ],[ 3.0, 4.0],[ 3.25, 3.75]]]]
element_RM8_T_core = [[ 0.09 , 'L' , 'XY' , [[ -2.3, 0.0 ],[ -2.3, 1.8],[ -3.0, 2.5 ],[ -1.0, 4.5 ]]]]
element_RM10_D_core = [[ 0.09 , 'L' , 'Diags' , [[ -1.8, 1.8],[ -1.2, 2.8],[ -1.2, 5.0 ],[ 2.5, 5.0],[ 3.8, 3.8]]]]
element_RM10_T_core = [[ 0.09 , 'L' , 'XY' , [[ -2.7, 0.0 ],[ -2.7, 1.3],[ -4.0, 2.8 ],[ -1.8, 5.5 ]]]]
element_RM12_D_core = [[ 0.09 , 'L' , 'Diags' , [[ -2.3, 2.3],[ -1.3, 3.5],[ -1.3, 6.0 ],[ 4.0, 6.0],[ 4.5, 4.5]]]]
element_RM12_T_core = [[ 0.09 , 'L' , 'XY' , [[ -3.2, 0.0 ],[ -3.2, 1.8],[ -5.0, 3.5 ],[ -1.0, 7.5 ]]]]
element_RM14_D_core = [[ 0.09 , 'L' , 'Diags' , [[ -2.5, 2.5],[ -1.0, 4.0],[ -1.0, 7.0 ],[ 5.0, 7.0],[ 6.0, 6.0]]]]
element_RM14_T_core = [[ 0.09 , 'L' , 'XY' , [[ -4.0, 0.0 ],[ -4.0, 2.8],[ -5.8, 4.0 ],[ -1.5, 7.7 ],[ 0.0, 7.7]]]]


# List of Pins
pin_RM5_D_4 = [[ 0.44 , 0.80, 'Cent' , [[ -1.0, 2.0 ],[ -2.0, 1.0 ] ]]]
pin_RM5_D_6 = [[ 0.44 , 0.80, 'Cent' , [[ -2.0, 2.0],[ -1.0, 2.0 ],[ -2.0, 1.0 ] ]]]
pin_RM5_D_8 = [[ 0.44 , 0.80, 'Cent' , [[ -2.0, 2.0],[ -1.0, 2.0 ],[ -2.0, 1.0 ],[ -1.0, 3.0 ] ]]]
pin_RM5_D_clip = [[ 0.55 , 0.91, 'Cent' , [[ -2.0, -2.0 ]]]]
pin_RM6_D_4 = [[ 0.44 , 0.80, 'Cent' , [[ -1.5, 2.5 ],[ -2.5, 1.5 ] ]]]
pin_RM6_D_6 = [[ 0.44 , 0.80, 'Cent' , [[ -2.5, 2.5],[ -1.5, 2.5 ],[ -2.5, 1.5 ] ]]]
pin_RM6_D_8 = [[ 0.44 , 0.80, 'Cent' , [[ -2.5, 2.5],[ -1.5, 2.5 ],[ -2.5, 1.5 ],[ -1.5, 3.5 ] ]]]
pin_RM6_D_clip = [[ 0.55 , 0.91, 'Cent' , [[ -2.5, -2.5 ]]]]
pin_RM6_T_8 = [[ 0.44 , 0.80, 'XY' , [[ 3.0, -2.5],[ 3.0, -1.0 ]]]]
pin_RM6_T_clip = [[ 0.55 , 0.91, 'Cent' , [[ 0, -3.5 ]]]]
pin_RM8_D_5 = [[ 0.44 , 0.80, 'Diags' , [[ -3.5, 1.5 ] ]],[ 0.44 , 0.56, 'None' , [[ -3.5, 2.5 ] ]]]
pin_RM8_D_8 = [[ 0.44 , 0.80, 'Diags' , [[ -3.5, 2.5],[ -3.5, 1.5 ] ]]]
pin_RM8_D_12 = [[ 0.44 , 0.80, 'Diags' , [[ -3.5, 2.5],[ -3.5, 1.5 ],[ -2.5, 1.5 ] ]]]
pin_RM8_D_clip = [[ 0.55 , 0.91, 'Cent' , [[ -3.5, -3.5 ]]]]
pin_RM8_T_12 = [[ 0.44 , 0.80, 'XY' , [[ 4.0, -4.0],[ 4.0, -2.5 ],[ 4.0, -1.0]]]]
pin_RM8_T_clip = [[ 0.55 , 0.91, 'Cent' , [[ 0, -5.0 ]]]]

pin_RM10_D_8 = [[ 0.44 , 0.80, 'Diags' , [[ -4.0, 3.0],[ -4.0, 2.0 ] ]]]
pin_RM10_D_12 = [[ 0.44 , 0.80, 'Diags' , [[ -4.0, 3.0],[ -4.0, 2.0 ],[ -3.0, 2.0 ] ]]]
pin_RM10_D_clip = [[ 0.55 , 0.91, 'Cent' , [[ -4.0, -4.0 ]]]]
pin_RM10_T_12 = [[ 0.69 , 1.05, 'XY' , [[ 5.5, -4.0],[ 5.5, -2.5 ],[ 5.5, -1.0]]]]
pin_RM10_T_clip = [[ 0.55 , 0.91, 'Cent' , [[ 0, -5.5 ]]]]

pin_RM12_D_12 = [[ 0.55 , 0.91, 'Diags' , [[ -5.5, 4.5],[ -5.5, 2.5 ],[ -3.5, 2.5 ] ]]]
pin_RM12_D_clip = [[ 0.55 , 0.91, 'Cent' , [[ -5.5, -5.5 ]]]]
pin_RM12_T_12 = [[ 0.68 , 1.05, 'XY' , [[ 6.5, -5.0],[ 6.5, -3.0 ],[ 6.5, -1.0]]]]
pin_RM12_T_clip = [[ 0.55 , 0.91, 'Cent' , [[ 0, -8.0 ]]]]

pin_RM14_D_12 = [[ 0.55 , 0.91, 'Diags' , [[ -6.5, 4.5],[ -6.5, 2.5 ],[ -4.5, 2.5 ] ]]]
pin_RM14_D_clip = [[ 0.69 , 1.05, 'Diags' , [[ -5.5, -7.5 ]]]]
pin_RM14_T_12 = [[ 0.69 , 1.05, 'XY' , [[ 7.0, -5.5],[ 7.0, -3.5 ],[ 7.0, -1.5]]]]
pin_RM14_T_clip = [[ 0.69 , 1.05, 'XY' , [[ -1.5, -9.0 ]]]]

# ... and the assembly
# each file has: aname, a center/offset, a pin construct list, a pin mapping list, a silk element list, a mark
element_global = [\
                  [ 'FERRIT', 'RM5_4D', [ 2.5 , 2.5 ], pin_RM5_D_4 + pin_RM5_D_clip , [6, 2, 3, 5], 9, element_RM5_D_core , [ -2.0, 1.0 ]],\
                  [ 'FERRIT', 'RM5_6D', [ 2.5 , 2.5 ], pin_RM5_D_6 + pin_RM5_D_clip , [1, 6, 2, 4, 3, 5], 9, element_RM5_D_core , [ -2.0, 2.0 ]],\
                  [ 'FERRIT', 'RM5_8D', [ 2.5 , 3.5 ], pin_RM5_D_8 + pin_RM5_D_clip , [1, 7, 2, 8, 5, 3, 6, 4], 9, element_RM5_D_core , [ -2.0, 2.0 ]],\
                  [ 'FERRIT', 'RM6_4D', [ 3.0 , 3.0 ], pin_RM6_D_4 + pin_RM6_D_clip , [6, 2, 3, 5], 9, element_RM6_D_core , [ -2.5, 1.5 ]],\
                  [ 'FERRIT', 'RM6_6D', [ 3.0 , 3.0 ], pin_RM6_D_6 + pin_RM6_D_clip , [1, 6, 2, 4, 3, 5], 9, element_RM6_D_core , [ -2.5, 2.5 ]],\
                  [ 'FERRIT', 'RM6_8D', [ 3.0 , 4.0 ], pin_RM6_D_8 + pin_RM6_D_clip , [1, 7, 2, 8, 5, 3, 6, 4], 9, element_RM6_D_core , [ -2.5, 2.5 ]],\
                  [ 'FERRIT', 'RM6_8T', [ 3.5 , 4.0 ], pin_RM6_T_8 + pin_RM6_T_clip , [1, 2, 4, 3, 5, 6, 8, 7], 9, element_RM6_T_core , [ 3.0, -2.5 ]],\
                  [ 'FERRIT', 'RM8_5D', [ 4.0 , 4.0 ], pin_RM8_D_5 + pin_RM8_D_clip , [2, 5, 8, 11, 1], 13, element_RM8_D_core , [ -3.5, 2.5 ]],\
                  [ 'FERRIT', 'RM8_8D', [ 4.0 , 4.0 ], pin_RM8_D_8 + pin_RM8_D_clip , [1, 2, 6, 5, 7, 8, 12, 11], 13, element_RM8_D_core , [ -3.5, 2.5 ]],\
                  [ 'FERRIT', 'RM8_12D', [ 4.0 , 4.0 ], pin_RM8_D_12 + pin_RM8_D_clip , [1, 2, 3, 6, 5, 4, 7, 8, 9, 12, 11, 10], 13, element_RM8_D_core , [ -3.5, 2.5 ]],\
                  [ 'FERRIT', 'RM8_12T', [ 3.5 , 4.0 ], pin_RM8_T_12 + pin_RM8_T_clip , [1, 2, 3, 6, 5, 4, 7, 8, 9, 12, 11, 10], 13, element_RM8_T_core , [ 4.0, -4.0 ]],\
                  [ 'FERRIT', 'RM10_8D', [ 4.0 , 4.0 ], pin_RM10_D_8 + pin_RM10_D_clip , [1, 2, 6, 5, 7, 8, 12, 11], 13, element_RM10_D_core , [ -4.0, 3.0 ]],\
                  [ 'FERRIT', 'RM10_12D', [ 4.0 , 4.0 ], pin_RM10_D_12 + pin_RM10_D_clip , [1, 2, 3, 6, 5, 4, 7, 8, 9, 12, 11, 10], 13, element_RM10_D_core , [ -4.0, 3.0 ]],\
                  [ 'FERRIT', 'RM10_12T', [ 3.5 , 4.0 ], pin_RM10_T_12 + pin_RM10_T_clip , [1, 2, 3, 6, 5, 4, 7, 8, 9, 12, 11, 10], 13, element_RM10_T_core , [ 5.5, -4.0 ]],\
                  [ 'FERRIT', 'RM12_12D', [ 4.0 , 4.0 ], pin_RM12_D_12 + pin_RM12_D_clip , [1, 2, 3, 6, 5, 4, 7, 8, 9, 12, 11, 10], 13, element_RM12_D_core , [ -5.5, 4.5 ]],\
                  [ 'FERRIT', 'RM12_12T', [ 3.5 , 4.0 ], pin_RM12_T_12 + pin_RM12_T_clip , [1, 2, 3, 6, 5, 4, 7, 8, 9, 12, 11, 10], 13, element_RM12_T_core , [ 6.5, -5.0 ]],\
                  [ 'FERRIT', 'RM14_12D', [ 4.0 , 4.0 ], pin_RM14_D_12 + pin_RM14_D_clip , [1, 2, 3, 6, 5, 4, 7, 8, 9, 12, 11, 10], 13, element_RM14_D_core , [ -6.5, 4.5 ]],\
                  [ 'FERRIT', 'RM14_12T', [ 3.5 , 4.0 ], pin_RM14_T_12 + pin_RM14_T_clip , [1, 2, 3, 6, 5, 4, 7, 8, 9, 12, 11, 10], 13, element_RM14_T_core , [ 7.0, -5.5 ]]\
                 ]

def main_symbol( of , descript ):
    gnd_index = 0
    of.write('Element(0x00 "' + descript[ 1 ] + ' description" "" "' + descript[ 1 ] + '" 160 0 3 100 0x00 )\n(\n' )
    center = XY_base( descript[ 2 ] , 100 )
    # Writing the pins
    ind_k = 0    # index to the mapping array
    for j,val in enumerate( descript[ 3 ] ):
        d1 = Widths( val[ 0 ])
        r1 = Widths( val[ 1 ])
        v1 = XY_list( val[ 3 ] , center )
        if val[ 2 ] == 'Diags': 
            v1.symetries_diagonal()
            v1.symetries_central()
        elif val[ 2 ] == 'XY' :
            v1.symetries_x_axis()
            v1.symetries_central()
        elif val[ 2 ] == 'Cent' :
            v1.symetries_central()
        for k,valP in enumerate( v1.elementPoint ):
            mapping = descript[ 4 ]
            if ind_k < len( mapping ):
                n1 = mapping[ ind_k ]
            else:
                n1 = descript[ 5 ] + gnd_index
                gnd_index += 1
            ind_k += 1
            write_pin( of , valP , r1 , d1 , n1 , o1 )
    # Writing elementLines 
    for l,val in enumerate( descript[ 6 ] ):
        elementWidth = Widths( val[0] )
        if val[ 1 ] == 'L':
            e1 = XY1XY2_list( val[ 3 ], center )
            if val[ 2 ] == 'Diags': 
                e1.symetries_diagonal()
                e1.symetries_central()
            elif val[ 2 ] == 'XY' :
                e1.symetries_x_axis()
                e1.symetries_central()
            elif val[ 2 ] == 'Cent' :
                e1.symetries_central()
    
            write_elements_list( of , e1 , elementWidth )
        else:
            print( '********** Some element are not yet supported **********' )
    # writing the mark
    v1 = XY( descript[ 7 ] , center )
    of.write( '\tMark(' + v1.export2string() + ')\n)\n' )


of_s = sys.stdout
for i,val in enumerate( element_global ):
    of_f = open( val[ 0 ] + '_' + val[ 1 ] + '.fp' , 'w' )
    main_symbol( of_f , val )
    main_symbol( of_s , val )
    of_f.close()


# of_i.write('#define output_size ' + str( len( crossover ) + 1 ) + '\n' )


