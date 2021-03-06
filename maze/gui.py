"""
Dude's Maze

The maze creator, generator and solver.
Choose your dude and let find his way towards the castle!

NEW! How long will you protect the castles from malituous dudes?
Change the maze and compare your best time with friends!

| Copyright © 2016 Lukáš Lopatovský

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

source: https://github.com/lopatovsky/Maze
All the graphic come from: http://opengameart.org/users/kenney
"""

import asyncio
from quamash import QEventLoop
from PyQt5 import QtWidgets, uic, QtGui, QtCore, QtSvg
import numpy
import glob
import os
import random
import math
import time
from docutils.core import publish_parts
from . import maze_generator, maze_solver, actor

CELL_SIZE = 32


class image:
    def __init__( self, name, path, num = -3 ):
        self.name = name
        self.path = path
        self.num = num
        self.svg = QtSvg.QSvgRenderer( self.path )

IMG = {}
NUM_INDEX = {}

for (item, num) in [ ('Grass',0), ('Wall',-1), ('Wall2',-2), ('Castle',1), ('Dude1',2), ('Dude2',3), ('Dude3',4), ('Dude4',5), ('Dude5',6) ]:
    IMG[ item ] = image( item, 'img/' + item.lower() + '.svg', num )
    NUM_INDEX[ num ] = IMG[item].svg

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


class GridWidget(QtWidgets.QWidget):

    def __init__(self, array, gui):

        super().__init__()
        self.gui = gui
        self.cell_size = CELL_SIZE
        self.array = array
        self.set_grid_size()

        self._solve()

    @property
    def play_mode( self ):
        return self.gui.play_action.isChecked()

    @play_mode.setter
    def play_mode(self, x):
        raise ValueError #TODO, not exactly value error

    def _ptol(self,x,y):
        return y // self.cell_size, x // self.cell_size

    def _ltop(self, row,column):
        return column * self.cell_size , row * self.cell_size

    def set_grid_size(self):
        # Bludiště může být jinak velké, tak musíme změnit velikost Gridu;
        rows, cols = self.array.shape
        size = self._ltop(rows, cols)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)


    def _solve(self):
        self.solved = maze_solver.analyze( self.array )
        self.directions = self.solved.directions


    def change_maze(self):
        self.set_grid_size()
        self._solve()
        self.update()

    def __get_paths(self):


        paths = numpy.full( (*self.array.shape,4)  , b'0', dtype=('a',1))

        dudes = numpy.argwhere(self.array >= 2)

        for dude in dudes:
            try:
                path = self.solved.path( *dude )
            except ValueError:
                continue

            get_in = DIR_TO_NUM[ self.directions[ path[0] ] ]  #first p doesn't have in, use out instead

            for p in path:
                #if paths[ (*p) , get_in ] == b'1': break #optimization for too many dudes
                paths[ (*p) , get_in ] = b'1'
                if self.directions[p] == b'X': break
                get_out = DIR_TO_NUM[ self.directions[p] ]
                paths[ (*p) , get_out ] = b'1'
                get_in = (get_out + 2 ) % 4   # 0->2, 1->3, 2->0, 3->1

        return paths

    def update_actor( self, actor ):

        x, y = self._ltop(actor.row, actor.column)
        rect = QtCore.QRect(x, y, int(self.cell_size), int(self.cell_size) )
        self.update( rect )

    def start_game( self ):

        self.dudes = []
        self.futures = []
        self.old_array = self.array.copy()
        self.last = (-1,-1) # (-1,-1) means no path for dude at the beginning of the game

        row_size, col_size = self.array.shape
        for row in range(row_size):
            for column in range(col_size):
                kind = self.array[row,column]
                if kind >= 2:
                    point = (row, column)
                    if kind == 2:
                        dude = actor.Right_hand_Actor(self, *point, self.array[row,column] )
                    elif kind == 3:
                        dude = actor.Confused_Actor(self, *point, self.array[row,column] )
                    elif kind == 4:
                        dude = actor.Fast_Actor(self, *point, self.array[row,column] )
                    elif kind == 5:
                        dude = actor.Accelerated_Actor(self, *point, self.array[row,column] )
                    elif kind == 6:
                        dude = actor.Teleported_Actor(self, *point, self.array[row,column] )

                    fut = asyncio.ensure_future( dude.behavior() )
                    self.futures.append(fut)
                    self.dudes.append( dude )


    def _end_game(self):
        for fut in self.futures:
            fut.cancel()
        self.array = self.old_array.copy()
        self.change_maze()


    def end_game( self , dialog_function = "final_time_dialog" ):
        self._end_game()
        self.gui.end_game( dialog_function )


    def no_path( self ):

        self.end_game( "no_suitable_path_dialog" )

    def _repaint_dudes( self, painter ):

        for dude in self.dudes:
            x, y = self._ltop(dude.row, dude.column)
            rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size )
            IMG[ "Dude"+ str(dude.kind - 1) ].svg.render(painter,rect)


    def paintEvent(self, event):


        painter = QtGui.QPainter(self)  #we will paint

        rect = event.rect()
        row_min, col_min = self._ptol(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = self._ptol(rect.right(),rect.bottom())
        row_max = min(row_max + 1, self.array.shape[0])
        col_max = min(col_max + 1, self.array.shape[1])

        row_size, col_size = self.array.shape

        if not self.play_mode:
            paths = self.__get_paths( )
            paths_view = paths.view('S4')


        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                # získáme čtvereček, který budeme vybarvovat
                x, y = self._ltop(row, column)
                rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size )

                #color = QtGui.QColor(255, 255, 255)

                # vyplníme čtvereček barvou
                #painter.fillRect(rect, QtGui.QBrush(color))

                #if self.play_mode:
                IMG['Grass'].svg.render(painter,rect)

                if not self.play_mode:

                    if paths_view[row,column][0] != b'0000':
                        LINES[ paths_view[row,column][0].decode("utf-8") ].svg.render(painter,rect)
                        if self.directions[row,column] != b'X':
                            ARROWS[ str(DIR_TO_NUM[self.directions[row,column] ])  ].svg.render(painter,rect)

                    if self.array[row,column] != 0 :
                        NUM_INDEX[self.array[row,column]].render(painter,rect)
                else:
                    if self.array[row,column] != 0 and self.array[row,column] < 2 :
                        NUM_INDEX[self.array[row,column]].render(painter,rect)

        if self.play_mode:
            self._repaint_dudes(painter)


    def wheelEvent(self, event):

        if event.modifiers() == QtCore.Qt.ControlModifier:
            degrees = event.angleDelta().y() / 8
            self.cell_size += round(self.cell_size*degrees/100)
            event.accept()
        else:
            event.ignore()

        self.set_grid_size()
        self.update()

    def can_put_wall(self, *point ):
        if self.array[point] < 0 or self.array[point] == 1: return
        for dude in self.dudes:

            for x in range ( int(math.floor(dude.row)), int(math.ceil(dude.row)) + 1 ):
                 for y in range ( int(math.floor(dude.column)), int(math.ceil(dude.column)) + 1 ):
                    if (x,y) == point: return

        self.array[point] = -1
        self._solve()


        for dude in self.dudes:
            if self.directions[ int(round( dude.row )), int( round(dude.column)) ] == b' ':
                self.array[point] = 0
                self._solve()
                return

        self.update()

    def mousePressEvent(self, event):

        row, column = self._ptol( event.x() , event.y() )

        shape = self.array.shape

        if 0 <= row < shape[0] and 0 <= column < shape[1]:

            if not self.play_mode:
                if event.button() == QtCore.Qt.LeftButton:
                        self.array[row,column] = self.selected

                elif event.button() == QtCore.Qt.RightButton:
                        self.array[row,column] = 0

                #todo only if changed
                self.change_maze()

            else:


                if event.button() == QtCore.Qt.LeftButton:
                    self.can_put_wall( row, column )

                elif event.button() == QtCore.Qt.RightButton:

                    if self.array[row,column] == -1:
                        self.array[row,column] = 0
                        self.change_maze()
                else:
                    return





class Gui():

    def __init__(self):

        self.app = QtWidgets.QApplication([])
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)


        self.window = QtWidgets.QMainWindow()
        #self.window.showFullScreen()


        with open ('GUI/mainwindow.ui') as f:
            uic.loadUi(f,self.window)

        array = numpy.zeros((10,13), dtype=numpy.int8 )
        self.grid = GridWidget(array, self)

        scroll_area = self.window.findChild(QtWidgets.QScrollArea, 'scrollArea') # alebo aj QtWidgets.Qwidget - dedi
        scroll_area.setWidget( self.grid )

        self._action( 'actionNew').triggered.connect( self._new_dialog )
        self._action( 'actionOpen').triggered.connect( self._open_dialog )
        self._action( 'actionSave').triggered.connect( self._save_dialog )
        self._action( 'actionAbout').triggered.connect( self._about_dialog )

        self._add_palette()


        self.play_action = self._action('actionPlay')
        self.play_action.triggered.connect( self._play )


        self.toolbar = self.window.findChild(QtWidgets.QToolBar, 'toolBar')
        self.running_timer = False



    def _action( self, action_name ):
        return self.window.findChild(QtWidgets.QAction, action_name )

    def _add_palette( self ):
        self.palette = self.window.findChild(QtWidgets.QListWidget, 'palette')
        self._fill_palette( )

    def _open_dialog(self):

        dialog = QtWidgets.QFileDialog(self.window)
        result = dialog.exec()

        if result == QtWidgets.QDialog.Rejected:
            return

        path = dialog.selectedFiles()[0]
        try:
            self.grid.array = numpy.loadtxt(path, dtype=numpy.int32)

        except OSError as e:
            self._alert_dialog( True, 'Error', 'File not found!', str(e), QtWidgets.QMessageBox.Warning )
            return
        except ValueError as e:
            self._alert_dialog( True, 'Error', 'Corrupted file!', str(e), QtWidgets.QMessageBox.Warning )
            return
        except IOError as e:
            self._alert_dialog( True, 'Error', 'Permission denied!', str(e), QtWidgets.QMessageBox.Warning )
            return
        except BaseException as e:
            self._alert_dialog( True, 'Weird Error', path , str(e), QtWidgets.QMessageBox.Warning )
            return

        self.grid.change_maze()

    async def _update_time(self):
            while True:
                #self.display.display(self.value)
                await asyncio.sleep(1)
                self.value += 1

    def final_time_dialog(self):
        game_time = time.time() - self.start_time - 1.0 # 1.0 - start jump time
        self._alert_dialog( True, "Game over!", "Your time was " + "{0:.2f}".format(game_time)  + " s." , "", QtWidgets.QMessageBox.Information )

    def no_suitable_path_dialog(self):

        self._alert_dialog( True, "Impossible to play!", "Some dudes can't find the path towards castle" , "", QtWidgets.QMessageBox.Warning )


    def end_game(self, dialog_function = "" ):

        self.play_action.setChecked(False)
        self.palette.show()
        self.item_activated()
        if dialog_function in dir(self):
            getattr(self, dialog_function)()

    def _play(self):

        self.grid.update()

        if self.play_action.isChecked():

            self.grid.selected = -1
            self.palette.hide()
            self.value = 0

            #if self.running_timer == False:
                #self.display = QtWidgets.QLCDNumber() #TODO display
                #self.toolbar.addWidget( self.display )
                #self.time_future = asyncio.ensure_future(self._update_time())
                #self.running_timer = True

            self.start_time = time.time()

            self.grid.start_game()

        else:
            self.grid.end_game("no_ending")

            #self.display.hide()


    def _alert_dialog(self, modal, title, text, detail, icon):

        dialog = QtWidgets.QMessageBox(self.window)

        dialog.setWindowTitle(title)
        dialog.setText(text)
        if detail != '': dialog.setDetailedText(detail)
        dialog.setIcon(icon)
        if modal:
            result = dialog.exec()

            if result == QtWidgets.QDialog.Rejected:
                return
        else:
            dialog.show()

    def _about_dialog( self ):

        html = publish_parts(__doc__, writer_name='html')['html_body']
        self._alert_dialog( False, 'About', html , '', QtWidgets.QMessageBox.Information )

    def _save_dialog(self):

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.window)

        if not path:
            return
        try:
            numpy.savetxt(path, self.grid.array )
        except BaseException as e:
            self._alert_dialog( True, 'Save Error', path , str(e), QtWidgets.QMessageBox.Warning )
            return


    def _new_dialog(self):

        dialog = QtWidgets.QDialog(self.window)
        with open ('GUI/newmaze.ui') as f:
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
            self.grid.array = maze_generator.generate_maze( cols, rows )
        else:
            self.grid.array = numpy.zeros((rows, cols), dtype=numpy.int32)


        self.grid.set_grid_size()

        self.grid.update() #TODO --when big resolution update only currently visible field

    def _add_item( self, palette, img ):

        item = QtWidgets.QListWidgetItem( img.name )
        icon = QtGui.QIcon( img.path )
        item.setIcon( icon )
        palette.addItem(item)
        item.setData( VALUE_ROLE, img.num )

    def item_activated( self ):
        for item in self.palette.selectedItems():
            self.grid.selected = item.data(VALUE_ROLE)
            #row_num = palette.indexFromItem(item).row()

    def _fill_palette( self ):


        for img in sorted(IMG.values(), key=lambda x: x.num ):
            self._add_item( self.palette, img )

        self.palette.itemSelectionChanged.connect(self.item_activated )
        self.palette.setCurrentRow(1)


    def run(self):
        self.window.show()
        return self.loop.run_forever()

def main():

    gui = Gui()
    return gui.run()


