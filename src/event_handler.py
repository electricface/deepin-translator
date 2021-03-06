#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from Xlib import X
from threading import Timer
from xutils import get_keyname, delete_selection, is_ctrl_key, is_alt_key, get_pointer_coordiante
import commands
from config import setting_config
from translate_window import get_active_view

class EventHandler(QObject):
    
    press_alt = pyqtSignal()
    release_alt = pyqtSignal()    
    press_ctrl = pyqtSignal()
    release_ctrl = pyqtSignal()
    
    press_esc = pyqtSignal()
    
    cursor_stop = pyqtSignal()

    left_button_press = pyqtSignal(int, int, int)
    right_button_press = pyqtSignal(int, int, int)    
    wheel_press = pyqtSignal()
    
    translate_selection = pyqtSignal(int, int, str)
    
    def __init__(self):
        QObject.__init__(self)

        self.press_alt_flag = False
        self.press_ctrl_flag = False

        self.stop_timer = None
        self.stop_delay = 0.05
        
        self.press_alt_timer = None
        self.press_alt_delay = 0.3

        self.press_ctrl_timer = None
        self.press_ctrl_delay = 0.5
        
        self.hover_flag = False
        
        self.double_click_flag = False
        self.double_click_counter = 0
        self.double_click_timeout = True
        self.double_reset_timer = None
        self.double_click_delay = 0.3
        
        # Delete selection first.
        delete_selection()
        
    def is_view_visible(self):
        view = get_active_view()

        if view == None:
            return False
        else:
            return view.isVisible()
        
    def is_cursor_in_view_area(self):
        view = get_active_view()
        if view == None:
            return False
        else:
            return view.in_translate_area()
        
    @pyqtSlot("QVariant")    
    def handle_event(self, event):
        if event.type == X.KeyPress:
            keyname = get_keyname(event)
            
            self.try_stop_timer(self.press_alt_timer)
            self.try_stop_timer(self.press_ctrl_timer)
        
            if is_alt_key(keyname):
                self.press_alt_flag = True
                
                if not setting_config.get_trayicon_config("pause"):
                    if not self.is_view_visible() or not self.is_cursor_in_view_area():
                        self.press_alt_timer = Timer(self.press_alt_delay, self.emit_press_alt)
                        self.press_alt_timer.start()
            elif is_ctrl_key(keyname):
                self.press_ctrl_flag = True
                
                if not setting_config.get_trayicon_config("pause"):
                    if not self.is_view_visible() or not self.is_cursor_in_view_area():
                        self.press_ctrl_timer = Timer(self.press_ctrl_delay, self.emit_press_ctrl)
                        self.press_ctrl_timer.start()
            elif keyname in ["Escape"]:
                self.press_esc.emit()
        elif event.type == X.KeyRelease:
            keyname = get_keyname(event)
            if is_alt_key(keyname):
                self.press_alt_flag = False
                self.release_alt.emit()
            elif is_ctrl_key(keyname):
                self.press_ctrl_flag = False
                self.release_ctrl.emit()
        elif event.type == X.ButtonPress:
            if event.detail == 1:
                self.left_button_press.emit(event.root_x, event.root_y, event.time)
                
                # Set hover flag when press.
                self.hover_flag = False    
                
                if self.double_click_timeout:
                    self.double_click_flag = False
                    self.double_click_timeout = False
                    self.double_click_counter = 0

                    self.double_reset_timer = Timer(self.double_click_delay, self.reset_double_click)
                    self.double_reset_timer.start()
                    
            elif event.detail == 3:
                self.right_button_press.emit(event.root_x, event.root_y, event.time)
            elif event.detail == 5:
                self.wheel_press.emit()
        elif event.type == X.ButtonRelease:
                
            self.double_click_counter += 1
            if self.double_click_counter == 2:
                if self.double_reset_timer != None:
                    self.try_stop_timer(self.double_reset_timer)
                    
                self.double_click_flag = True
                self.double_click_timeout = True

            # import time    
            if not self.is_view_visible() or not self.is_cursor_in_view_area():
                # print "1", time.time()
                # Trigger selection handle if mouse hover or double click.
                if self.hover_flag or self.double_click_flag:
                    if not setting_config.get_trayicon_config("pause"):
                        if not setting_config.get_trayicon_config("key_trigger_select") or self.press_ctrl_flag:
                            self.translate_selection_area()
            # Delete clipboard selection if user selection in visible area to avoid next time to translate those selection content.
            elif self.is_view_visible() and self.is_cursor_in_view_area():
                # print "2", time.time()
                delete_selection()
                
            self.hover_flag = False    
        elif event.type == X.MotionNotify:
            # Set hover flag to prove selection action.
            self.hover_flag = True
            
            self.try_stop_timer(self.stop_timer)
        
            if not setting_config.get_trayicon_config("pause"):
                self.stop_timer = Timer(self.stop_delay, lambda : self.emit_cursor_stop(event.root_x, event.root_y))
                self.stop_timer.start()                    
                    
    def reset_double_click(self):
        self.double_click_flag = False
        self.double_click_timeout = True
                
    def emit_cursor_stop(self, mouse_x, mouse_y):
        if self.press_alt_flag and (not self.is_view_visible() or not self.is_cursor_in_view_area()):
            self.cursor_stop.emit()
            
    def emit_press_ctrl(self):
        self.press_ctrl.emit()

    def emit_press_alt(self):
        self.press_alt.emit()

    def try_stop_timer(self, timer):
        if timer and timer.is_alive():
            timer.cancel()
            
    def translate_selection_area(self):
        selection_content = commands.getoutput("xsel -p -o")
        delete_selection()
                            
        if len(selection_content) > 1 and not selection_content.isspace():
            (mouse_x, mouse_y) = get_pointer_coordiante()
            self.translate_selection.emit(mouse_x, mouse_y, selection_content)
        
            
