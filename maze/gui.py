from PyQt5 import QtWidgets, uic, QtGui, QtCore, QtSvg
import numpy
from maze import maze_generator, maze_solver

CELL_SIZE = 32

class image:
    def __init__( self, name, path, num ):
        self.name = name
        self.path = path
        self.num = num
        self.svg = QtSvg.QSvgRenderer( self.path )

IMG = {}

for (item, num) in [ ('Grass',0), ('Wall',-1), ('Wall2',-2), ('Castle',1), ('Dude1',2), ('Dude2',3), ('Dude3',4), ('Dude4',5), ('Dude5',6) ]:
    IMG[ item ] = image( item, 'img/' + item.lower() + '.svg', num )

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

    '''def paintEvent( self, event):

        rect = event.rect()
        painter = QtGui.QPainter(self)  #paint to anything
        color = QtGui.QColor(0,75,0)
        painter.fillRect(rect, color )'''

    def paintEvent(self, event):
        rect = event.rect()  # získáme informace o překreslované oblasti

        # zjistíme, jakou oblast naší matice to představuje
        # nesmíme se přitom dostat z matice ven
        row_min, col_min = ptol(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = ptol(rect.right(), rect.bottom())
        row_max = min(row_max + 1, self.array.shape[0])
        col_max = min(col_max + 1, self.array.shape[1])

        painter = QtGui.QPainter(self)  # budeme kreslit

        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                # získáme čtvereček, který budeme vybarvovat
                x, y = ltop(row, column)
                rect = QtCore.QRectF(x, y, CELL_SIZE, CELL_SIZE)

                # šedá pro zdi, zelená pro trávu
                color = QtGui.QColor(255, 255, 255)

                # vyplníme čtvereček barvou
                painter.fillRect(rect, QtGui.QBrush(color))

                IMG['Grass'].svg.render(painter,rect)

                for img in IMG.values():
                    if self.array[row, column] == img.num:
                        img.svg.render(painter,rect)

    def mousePressEvent(self, event):
        row, column = ptol( event.x() , event.y() )

        shape = self.array.shape

        if 0 <= row < shape[0] and 0 <= column < shape[1]:
            if event.button() == QtCore.Qt.LeftButton:
                self.array[row,column] = self.selected
            elif event.button() == QtCore.Qt.RightButton:
                self.array[row,column] = 0
            else:
                return

            self.update(*ltop(row,column), CELL_SIZE, CELL_SIZE ) # or self.update()  -- update all




def new_dialog(window,grid):

    dialog = QtWidgets.QDialog(window)
    with open ('newmaze.ui') as f:
        uic.loadUi(f,dialog)
    result = dialog.exec()

    if result == QtWidgets.QDialog.Rejected:
        # Dialog uživatel zavřel nebo klikl na Cancel
        return

    # Načtení hodnot ze SpinBoxů
    cols = dialog.findChild(QtWidgets.QSpinBox, 'widthBox').value()
    rows = dialog.findChild(QtWidgets.QSpinBox, 'heightBox').value()
    random = dialog.findChild(QtWidgets.QCheckBox, 'randomcheckBox').isChecked()  #TODO QButtonGroup + empty, file

    # Vytvoření nového bludiště
    if random:
        grid.array = maze_generator.generate_maze( rows, cols )
    else:
        grid.array = numpy.zeros((rows, cols), dtype=numpy.int8)

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

    array = numpy.zeros((20,20), dtype=numpy.int8 )
    grid = GridWidget(array)

    scroll_area = window.findChild(QtWidgets.QScrollArea, 'scrollArea') # alebo aj QtWidgets.Qwidget - dedi
    scroll_area.setWidget( grid )

    action = window.findChild(QtWidgets.QAction, 'actionNew')
    action.triggered.connect(lambda: new_dialog(window,grid) )

    palette = window.findChild(QtWidgets.QListWidget, 'palette')
    fill_palette( palette, grid )

    window.show()
    return app.exec()

