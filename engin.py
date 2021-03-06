from PyQt4 import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt
from OpenGL import *
from scene import *
import time
import random


class Engin(QtOpenGL.QGLWidget):
   def __init__(self, parent=None):
      super(Engin, self).__init__(parent)


   def init(self):
      self.key_w    = False
      self.key_a    = False
      self.key_s    = False
      self.key_d    = False
      self.key_up   = False
      self.key_down = False

      self.setFocusPolicy(Qt.ClickFocus)

      glClearColor(0.0618, 0.0618, 0.0618, 1.0)
      glClearDepth(1.0)
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

      glPolygonMode(GL_FRONT, GL_FILL)
      glPolygonMode(GL_BACK, GL_FILL)

      glShadeModel(GL_SMOOTH)

      glLightfv(GL_LIGHT0, GL_POSITION, (0, 1, 1, 0))

      glEnable(GL_DEPTH_TEST)
      glEnable(GL_CULL_FACE)
      glEnable(GL_LIGHTING)
      glEnable(GL_LIGHT0)

      #glEnable(GL_TEXTURE_2D)
      glEnable(GL_BLEND)
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      #glEnable(GL_NORMALIZE);

      glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (1, 1, 1, 1))

      glEnableClientState(GL_VERTEX_ARRAY)
      glEnableClientState(GL_NORMAL_ARRAY)
      #glEnableClientState(GL_TEXTURE_COORD_ARRAY)

      self.scene = Scene()
      self.last_frame = time.time()

      self.load_textures()

      timer = QtCore.QTimer(self)
      timer.timeout.connect(self.cycle)
      timer.start(60)


   def initializeGL(self):
      self.init()


   def cycle(self):
      self.update()
      self.paint()


   def update(self):
      dt = time.time() - self.last_frame

      self.update_keyboard(dt)
      self.scene.update(dt)

      # Check collisions
      def distance(obj1, obj2):
         dist = ((obj1.x - obj2.x) ** 2 + (obj1.y - obj2.y)**2 + (obj1.z - obj2.z)**2) ** 0.5
         return dist
      for bullet in self.scene.player.bullets:
         if self.scene.target and distance(bullet.position, self.scene.target.position) < 1:
            self.scene.target = Target(Vector3(random.randint(0, 10), 1, random.randint(0, 10)))
            self.scene.player.bullets.remove(bullet)
            break

      self.last_frame = time.time()


   def paint(self):
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

      self.scene.paint()

      self.swapBuffers()




   def load_textures(self):
      im = open('textures/skybox.jpg')
      ix, iy, image = im.size[0], im.size[1], im.tostring("raw", 'RGBX', 0, -1)
      self.id = 0
      id = glGenTextures(1)
      glBindTexture(GL_TEXTURE_2D, id)
      glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
      glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
      glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)


   def update_keyboard(self, dt):
      if self.key_w:    self.scene.player.walk_forward(dt)
      if self.key_s:    self.scene.player.walk_backward(dt)
      if self.key_a:    self.scene.player.walk_left(dt)
      if self.key_d:    self.scene.player.walk_right(dt)
      if self.key_up:   self.scene.player.camera.pitch += 10 * dt
      if self.key_down: self.scene.player.camera.pitch -= 10 * dt


   def keyPressEvent(self, evt):
      if evt.key() == Qt.Key_W:    self.key_w    = True
      if evt.key() == Qt.Key_A:    self.key_a    = True
      if evt.key() == Qt.Key_S:    self.key_s    = True
      if evt.key() == Qt.Key_D:    self.key_d    = True
      if evt.key() == Qt.Key_Up:   self.key_up   = True
      if evt.key() == Qt.Key_Down: self.key_down = True


   def keyReleaseEvent(self, evt):
      if evt.key() == Qt.Key_W:    self.key_w    = False
      if evt.key() == Qt.Key_A:    self.key_a    = False
      if evt.key() == Qt.Key_S:    self.key_s    = False
      if evt.key() == Qt.Key_D:    self.key_d    = False
      if evt.key() == Qt.Key_Up:   self.key_up   = False
      if evt.key() == Qt.Key_Down: self.key_down = False


   def focusInEvent(self, evt):
      self.setCursor(QtGui.QCursor(Qt.BlankCursor))


   def focusOutEvent(self, evt):
      print "FOCUSOUT"


   def mousePressEvent(self, evt):
      self.scene.player.fire()
      pass


   def mouseReleaseEvent(self, evt):
      print "MR"
      pass


   def mouseMoveEvent(self, *args, **kwargs):
      evt = args[0]

      if self.hasFocus() and len(args) > 1:
         window_x = args[1]
         window_y = args[2]
         pos = evt.pos()
         wcx = window_x + 800.0/2
         wcy = window_y + 600.0/2

         cam = self.scene.player.camera

         x = pos.x() / (800.0/2)
         y = (pos.y() + 22) / (600.0/2)
         x = x - 1
         y = 1 - y

         q = Quaternion.new_rotate_axis(-x * math.pi, Vector3(0, 1, 0))
         cam.focus = cam.focus - cam.position
         cam.focus = q * cam.focus
         cam.focus = cam.focus + cam.position

         QtGui.QCursor.setPos(wcx, wcy)


   def wheelEvent(self, evt):
      pass


   def sizeHint(self):
      return QtCore.QSize(800, 600)


   def resizeGL(self, width, height):
      self.scene.player.camera.viewport(width, height)
      self.scene.player.camera.update()
