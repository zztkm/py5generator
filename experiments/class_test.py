import py5
from py5 import Py5Applet


class Test(Py5Applet):

    def settings(self):
        self.size(500, 600, py5.P2D)

    def setup(self):
        self.background(255)
        self.rect_mode(py5.CENTER)
        self.frame_rate(30)

    def draw(self):
        if self.is_key_pressed():
            print('frameRate', self.get_frame_rate())
        self.fill(self.random(255), self.random(255), self.random(255), 50.0)
        self.rect(self.mouse_x, self.mouse_y, 40, 40)


test = Test()
test.run_sketch()
