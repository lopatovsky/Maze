from PyQt5 import QtWidgets, uic, QtGui, QtCore, QtSvg
import numpy
import glob
import os
from maze import maze_generator, maze_solver

CELL_SIZE = 16

class image:
    def __init__( self, name, path, num = -1 ):
        self.name = name
        self.path = path
        self.num = num
        self.svg = QtSvg.QSvgRenderer( self.path )

IMG = {}

for (item, num) in [ ('Grass',0), ('Wall',-1), ('Wall2',-2), ('Castle',1), ('Dude1',2), ('Dude2',3), ('Dude3',4), ('Dude4',5), ('Dude5',6) ]:
    IMG[ item ] = image( item, 'img/' + item.lower() + '.svg', num )

LINES = {}
for item in glob.glob('img/lines/*.svg'):
    name = os.path.splitext( os.path.basename(item) )[0]
    LINES[ name ] = image( name, item)

ARROWS = {}
for item in glob.glob('img/arrows/*.svg'):
    name = os.path.splitext( os.path.basename(item) )[0]
    ARROWS[ name ] = image( name, item)

DIR_TO_NUM = {b'^':0,b'>':1,b'v':2,b'<':3}

VALUE_ROLE = QtCore.Qt.UserRole

def ptol(x,y):
    return y // CELL_SIZE, x // CELL_SIZE
def ltop(row,column):
    return column * CELL_SIZE , row * CELL_SIZE

class GridWidget(QtWidgets.QWidget):

    def __init__(self, array):

        super().__init__()
        self.array = array
        size = ltop(*array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)


    def __get_paths(self, solved):


        paths = numpy.full( (*self.array.shape,4)  , b'0', dtype=('a',1))
        directions = solved.directions

        dudes = numpy.argwhere(self.array >= 2)

        for dude in dudes:
            try:
                path = solved.path( *dude )
            except ValueError:
                continue

            get_in = DIR_TO_NUM[ directions[ path[0] ] ]  #first p doesn't have in, use out instead

            for p in path:
                paths[ (*p) , get_in ] = b'1'
                if directions[p] == b'X': break
                get_out = DIR_TO_NUM[ directions[p] ]
                paths[ (*p) , get_out ] = b'1'
                get_in = (get_out + 2 ) % 4   # 0->2, 1->3, 2->0, 3->1

        return paths

    def paintEvent(self, event):
        #TODO: more castles?

        print('paint')

        row_size, col_size = self.array.shape

        solved = maze_solver.analyze( self.array )
        directions = solved.directions

        paths = self.__get_paths( solved )

        painter = QtGui.QPainter(self)  # budeme kreslit

        paths_view = paths.view('S4')

        for row in range(row_size):
            for column in range(col_size):
                # získáme čtvereček, který budeme vybarvovat
                x, y = ltop(row, column)
                rect = QtCore.QRectF(x, y, CELL_SIZE, CELL_SIZE)

                color = QtGui.QColor(255, 255, 255)

                # vyplníme čtvereček barvou
                painter.fillRect(rect, QtGui.QBrush(color))

                IMG['Grass'].svg.render(painter,rect)

                if paths_view[row,column][0] != b'0000':
                    LINES[ paths_view[row,column][0].decode("utf-8") ].svg.render(painter,rect)
                    if directions[row,column] != b'X':
                        ARROWS[ str(DIR_TO_NUM[directions[row,column] ])  ].svg.render(painter,rect)

                #TODO - space for more effective approach
                if self.array[row,column] != 0:
                    for img in IMG.values():
                        if self.array[row, column] == img.num:
                            img.svg.render(painter,rect)




    def mousePressEvent(self, event):

        print('press')
        row, column = ptol( event.x() , event.y() )

        shape = self.array.shape

        if 0 <= row < shape[0] and 0 <= column < shape[1]:
            if event.button() == QtCore.Qt.LeftButton:
                self.array[row,column] = self.selected
            elif event.button() == QtCore.Qt.RightButton:
                self.array[row,column] = 0
            else:
                return

            self.update()




def new_dialog(window,grid):

    dialog = QtWidgets.QDialog(window)
    with open ('newmaze.ui') as f:
        uic.loadUi(f,dialog)
    result = dialog.exec()

    if result == QtWidgets.QDialog.Rejected:
        # Dialog uživatel zavřel nebo klikl na Cancel
        return

    # Načtení hodnot ze SpinBoxů
    cols = dialog.findChild(QtWidgets.QSpinBox, 'widthBox').value()  #TODO stale to je stvorec!?
    rows = dialog.findChild(QtWidgets.QSpinBox, 'heightBox').value()
    random = dialog.findChild(QtWidgets.QCheckBox, 'randomcheckBox').isChecked()  #TODO QButtonGroup + empty, file

    # Vytvoření nového bludiště
    if random:
        grid.array = maze_generator.generate_maze( rows, cols )
    else:
        grid.array = numpy.zeros((rows, cols), dtype=numpy.int32)

    # Bludiště může být jinak velké, tak musíme změnit velikost Gridu;
    # (tento kód používáme i jinde, měli bychom si na to udělat funkci!)
    size = ltop(rows, cols)
    grid.setMinimumSize(*size)
    grid.setMaximumSize(*size)
    grid.resize(*size)


def add_item( palette, img ):

    item = QtWidgets.QListWidgetItem( img.name )
    icon = QtGui.QIcon( img.path )
    item.setIcon( icon )
    palette.addItem(item)
    item.setData( VALUE_ROLE, img.num )

def fill_palette( palette, grid ):


    for img in sorted(IMG.values(), key=lambda x: x.num ):
        add_item( palette, img )

    def item_activated( ):
        for item in palette.selectedItems():
            grid.selected = item.data(VALUE_ROLE)
            #row_num = palette.indexFromItem(item).row()

    palette.itemSelectionChanged.connect(item_activated )
    palette.setCurrentRow(1)


def main():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    with open ('mainwindow.ui') as f:
        uic.loadUi(f,window)

        #TODO generator generuje len liche/sude
    array = numpy.zeros((10,10), dtype=numpy.int8 )
    grid = GridWidget(array)

    scroll_area = window.findChild(QtWidgets.QScrollArea, 'scrollArea') # alebo aj QtWidgets.Qwidget - dedi
    scroll_area.setWidget( grid )

    action = window.findChild(QtWidgets.QAction, 'actionNew')
    action.triggered.connect(lambda: new_dialog(window,grid) )

    palette = window.findChild(QtWidgets.QListWidget, 'palette')
    fill_palette( palette, grid )

    window.show()
    return app.exec()

