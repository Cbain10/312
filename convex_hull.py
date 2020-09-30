from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False
		
# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)
		
	def eraseHull(self,polygon):
		self.view.clearLines(polygon)
		
	def showText(self,text):
		self.view.displayStatusText(text)
	

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		def getXVal(obj):
			return obj.x()
		points.sort(key = getXVal)
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		#polygon is simply a list of QLineF objects
		# polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		polygon = self.solveConvexHull(points)

		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def solveConvexHull(self, points):		# FIXME recursion issues - not reaching base case
		if len(points) == 1:
			print("reached the base case")
			line = QLineF(points[0],points[0])
			hull = [line]
			return hull			# FIXME return a list of single QLineF object?
		n = len(points)
		x = self.solveConvexHull(points[0: ((n//2)-1)])		# FIXME not reaching base case for odd numbers
		print("finished X")
		y = self.solveConvexHull(points[(n//2): n - 1])
		print("finished Y")
		result = self.combineHulls(x, y)
		return result

	def combineHulls(self, h1, h2):
		line1 = self.findUpperTangent(h1, h2)		# returns a single QLineF object
		line2 = self.findLowerTangent(h1, h2)		# returns a single QLineF object
		newHull = []
		newHull.append(line1)
		tempPoint = line1.p2()
		# go through lines in right hull, add to new list
		# FIXME - wont always start with correct line in hull - needs to be cicrular list
		# iterate 2n - 1 times? always guaranteed to find all the lines before combining hulls
		for edge in h2:
			if edge.p1() == tempPoint:
				newHull.append(edge)
				tempPoint = edge.p2()
			if tempPoint == line2.p1():
				break
		newHull.append(line2)
		tempPoint = line2.p2()
		for edge in h1:
			if edge.p1() == tempPoint:
				newHull.append(edge)
				tempPoint = edge.p2()
			if tempPoint == line1.p1():
				break
		return newHull

	def findUpperTangent(self, hull1, hull2):
		p = self.findRightMostPoint(hull1)
		q = self.findLeftMostPoint(hull2)
		h1Size = len(hull1)
		h2Size = len(hull2)
		tempLine = QLineF(hull1[p%h1Size].p2(),hull2[q%h2Size].p2())		#FIXME x2() vs p2()!!!! ????
		tangentFound = 0
		while tangentFound == 0:
			tangentFound = 1
			# LEFT Hull
			while tempLine.dy()/tempLine.dx() > QLineF(hull1[(p-1)%h1Size].p2(),hull2[q%h2Size].p2()).dy()/QLineF(hull1[(p-1)%h1Size].p2(),hull2[q%h2Size].p2()).dx():
				r = p - 1
				tempLine = QLineF(hull1[r%h1Size].p2(),hull2[q%h2Size].p2())
				p = r
				tangentFound = 0
			# RIGHT Hull
			while tempLine.dy()/tempLine.dx() < QLineF(hull1[p%h1Size].p2(),hull2[(q+1)%h2Size].p2()).dy()/QLineF(hull1[p%h1Size].p2(),hull2[(q+1)%h2Size].p2()).dx():
				r = q + 1
				tempLine = QLineF(hull1[p%h1Size].p2(),hull2[r%h2Size].p2())
				q = r
				tangentFound = 0
		return tempLine


	def findLowerTangent(self, hull1, hull2):
		p = self.findRightMostPoint(hull1)
		q = self.findLeftMostPoint(hull2)
		h1Size = len(hull1)
		h2Size = len(hull2)
		tempLine = QLineF(hull1[p%h1Size].p2(),hull2[q%h2Size].p2())
		tangentFound = 0
		while tangentFound == 0:
			tangentFound = 1
			# LEFT Hull
			while tempLine.dy()/tempLine.dx() < QLineF(hull1[(p+1)%h1Size].p2(),hull2[q%h2Size].p2()).dy()/QLineF(hull1[(p+1)%h1Size].p2(),hull2[q%h2Size].p2()).dx():
				r = p + 1
				tempLine = QLineF(hull1[r%h1Size].p2(),hull2[q%h2Size].p2())
				p = r
				tangentFound = 0
			# RIGHT hull
			while tempLine.dy()/tempLine.dx() > QLineF(hull1[p%h1Size].p2(),hull2[(q-1)%h2Size].p2()).dy()/QLineF(hull1[p%h1Size].p2(),hull2[(q-1)%h2Size].p2()).dx():
				r = q - 1
				tempLine = QLineF(hull1[p%h1Size].p2(),hull2[r%h2Size].p2())
				q = r
				tangentFound = 0
		return tempLine


	def findRightMostPoint(self, hull):
		p = 0
		for i in range(len(hull) - 1):
			if hull[i].x2() > p:
				p = i
		return p

	def findLeftMostPoint(self, hull):
		q = 0
		for i in range(len(hull) - 1):
			if hull[i].x2() < q:
				q = i
		return q

	def myTestMethod(self, points):
		myList = []
		size = len(points)
		line1 = QLineF(points[0%size],points[1%size])
		line2 = QLineF(points[1%size],points[2%size])
		line3 = QLineF(points[2%size],points[3%size])
		line4 = QLineF(points[3%size],points[4%size])
		line5 = QLineF(points[4%size], points[5%size])
		myList.append(line1)
		myList.append(line2)
		myList.append(line3)
		myList.append(line4)
		myList.append(line5)
		return myList
