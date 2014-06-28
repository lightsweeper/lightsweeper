### Implementation of a single lightsweeper tile

class Tile:
	def __init__(self, row=0, col=0):
		self.x = col
		self.y = row
		return

	def destroy(self):
		return

	def setColor(self, color):
		return

	def setShape(self, shape):
		return

	def setTransition(self, transition):
		return

	def set(self,color=0, shape=0, transition=0):
		if (color != 0)
			self.setColor(color)
		if (shape != 0 )
			self.setShape(shape)
		if(transition != 0)
			self.setTransition(transition)
		return

	def update(self,type):
		if (type == 'NOW'):
			return
		elif (type == 'CLOCK'):
			return
		elif (type == 'TRIGGER'):
			return
		else
			return

	def version(self):
		return 1

	def blank(self):
		return

	def locate(self):
		return

	def demo (int seconds):
		return

	def setAnimation(self):
		return

	def flip(self):
		return

	def status(self):
		return

	def reset(self):
		return

	def latch(self):
