import numpy as np
# import PIL
from dataclasses import dataclass
import random

UP = 0 # help how do i do constants
RIGHT = 1
DOWN = 2
LEFT = 3


@dataclass
class tile:
	id:int
	size:int
	sides:list
	srcpath:str = ''

# to be moved to own file - mostly
metaconfig = {
'DIM': 5,
'ENTROPY_PASSES': 3,
# 'SEED': 0,
'TILESIZE': 8,
'TILES': [
		{
		'src': '',
		'sides': ['aaa', 'aaa', 'aaa', 'bbb'],
		'rotation': 4
		},
		{
		'src': '',
		'sides': ['aaa', 'bbb', 'aaa', 'bbb'],
		'rotation': 2
		},
		{
		'src': '',
		'sides': ['bbb', 'bbb', 'bbb', 'aaa'],
		'rotation': 4
		},
		{
		'src': '',
		'sides': ['aaa', 'aaa', 'aaa', 'aaa'],
		'rotation': 1
		},
		{
		'src': '',
		'sides': ['bbb', 'bbb', 'bbb', 'bbb'],
		'rotation': 1
		},
		{
		'src': '',
		'sides': ['aaa', 'aaa', 'bbb', 'bbb'],
		'rotation': 4
		}
	]
}

def p():
		global grid
		t = grid[:].flatten().tolist()
		print('---------------')
		t.sort(key=lambda x: x.pos)
		print(*t, sep='\n')

		for i in grid:
			for j in i:
				print(j.pos, j.tile)
				pass

# works so far
def rotate(tile, rotation):
	# todo: add image processing and rotation
	newtile = {**tile}
	for i in range(rotation):
		newUP = newtile['sides'][-1][::-1]
		newtile['sides'] = [newUP] + [newtile['sides'][0], newtile['sides'][1][::-1], newtile['sides'][2]]
	del newtile['rotation']
	return newtile
		

try:
	random.seed(metaconfig['SEED'])
except KeyError:
	pass
alltiles = []
allpossibilities = []
for t in metaconfig['TILES']:
	for i in range(t['rotation']):
		alltiles.append(rotate(t, i))
		allpossibilities.append(alltiles[-1]['sides'])


@dataclass
class cell:
	id:int
	pos:tuple
	neighbours:dict
	possibilities = allpossibilities
	entropy:int = len(possibilities)
	collapsed = False
	tile = None

	
cell.__str__ = lambda self: f'id: {self.id}, pos: {self.pos}, neighbours: {"{...}"}, entropy: {self.entropy}, collapsed: {self.collapsed}'


# works
def makeadjacencies(elem, grid):
	# top, right, down, left
	# don't question it if it works
	for i in [1, 2, 3, 4]:
		d = -1 if i<3 else 1
		try:
			nextCell = grid[elem.pos[1] + (i % 2) * d, elem.pos[0] + ((i + 1) % 2) * (-d)]
		except IndexError:
			# wraparound
			if elem.pos[1] + (i % 2) * d < 0:
				nexty = metaconfig['DIM'] - 1
			elif elem.pos[1] + (i % 2) * d == metaconfig['DIM']:
				nexty = 0
			else:
				nexty = elem.pos[1] + (i % 2) * d
			if elem.pos[0] + ((i + 1) % 2) * (-d) < 0:
				nextx = metaconfig['DIM']
			elif elem.pos[0] + ((i + 1) % 2) * (-d) == metaconfig['DIM']:
				nextx = 0
			else:
				nextx = elem.pos[0] + ((i + 1) % 2) * (-d)
				
			nextCell = grid[nexty, nextx]
		finally:
			elem.neighbours |= {i - 1: nextCell}
			


# didnt work yet, nuked it
# todo: finish func
def reduceEntropy(cell):
	ncpl = []
	n0, n1, n2, n3 = cell.neighbours.values()
	
	for poss in cell.possibilities:
		i = False
		
		for nup in n0.possibilities:
			if poss[UP] != nup[DOWN][::-1]:
				continue
				
			for nrp in cell.neighbours[1].possibilities:
				if poss[RIGHT] != nrp[LEFT][::-1]:
					continue
				for ndp in cell.neighbours[2].possibilities:
					if poss[DOWN] != ndp[UP]:
						continue
					for nlp in cell.neighbours[3].possibilities:
						if poss[LEFT] != nlp[RIGHT]:
							continue
						# this looks ugly as shit but at this point i dont care
						ncpl.append(poss)
						i = True
						# 5 loops
						break
					# 4 loops
					if i: break
				# 3 loops
				if i: break
			# 2 loops
			if i: break
		# 1 loop
	# no loop

	cell.possibilities = ncpl
	cell.entropy = len(ncpl)
	return cell

# works? - works
def lowestEntropy(g):
	# filter out all collapsed cells
	temp = [*filter(lambda x: not x.collapsed, g[:].flatten().tolist())]
	# if we done, we done
	if not len(temp):
		return []
	# s o r t
	temp.sort(key=lambda x: x.entropy)
	
	lowest = temp[0].entropy
	lowest_poss = []
	# get possition of cells with lowest entropy
	for i in temp:
		if i.entropy == lowest:
			lowest_poss.append(i.pos)
	# return lowest entropy as well as the cells
	return [lowest, lowest_poss]
	
	

def main_loop(grid):
	while True:
		e = lowestEntropy(grid)
		if len(e) == 0:
			print('done')
			p()
			break
		modifyPos = random.choice(e[1])
		modifyCell = grid[modifyPos[1], modifyPos[0]]
		t = random.choice(modifyCell.possibilities)
		modifyCell.tile = t
		modifyCell.possibilities = [t]
		modifyCell.entropy = 1
		modifyCell.collapsed = True
		
		for i in range(metaconfig['ENTROPY_PASSES']):
			for row in grid:
				for cell in row:
					grid[cell.pos[1], cell.pos[0]] = reduceEntropy(cell)
					
			# print(f'Entropy pass {i} done')
					
		p()
		# grid good here?
		




if __name__ =='__main__':
	grid = []
	for i in range(metaconfig['DIM']**2):
		grid.append(cell(i, (i % metaconfig['DIM'], i // metaconfig['DIM']), {}))

# 2d array of size n by n
	grid = np.array(grid)
	grid = np.reshape(grid, (metaconfig['DIM'], metaconfig['DIM']))
	
	for row in grid:
		for cell in row:
			makeadjacencies(cell, grid)


	# grid fine here
	main_loop(grid)
# import promise
# print(promise.Promise(lambda x, y: print(x, y)))
# Dont think i need this
# dataclass go 'b' + 'r'*4
# todo: set constants as such
# todo: main loop and resolving grid