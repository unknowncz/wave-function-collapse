import numpy as np
from PIL import Image
from dataclasses import dataclass
import random

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


@dataclass
class tile:
	id:int
	size:int
	sides:list
	srcpath:str = ''
	img:Image = None

metaconfig = {
**eval(open(f'{__file__}\\..\\metadata.txt').read()),
# yeah yeah insecure but whatever
'TILES': eval(open(f'{__file__}\\..\\tiles.txt').read())
}

def p():
	global grid
	t = grid[:].flatten().tolist()
	print('---------------')
	t.sort(key=lambda x: x.pos)
	print(*t, sep='\n')
	print('---------------')
	for i in grid:
		for j in i:
			print(j.pos, j.tile)

# works so far - does it?

def rotate(tile, rotation):
	t = {**tile}
	# rotate tile
	t['img'] = t['img'].rotate(rotation * 90)
	# get new sides
	for i in range(rotation):
		t['sides'] = [t['sides'][1], t['sides'][2][::-1], t['sides'][3], t['sides'][0][::-1]]
	return t

try:
	random.seed(metaconfig['SEED'])
except KeyError:
	pass
alltiles = []
allpossibilities = []
for t in metaconfig['TILES']:
	if t["src"]:
		t['img'] = Image.open(f'{__file__}\\..\\{t["src"]}')
	for i in range(t['rotation']):
		alltiles.append(rotate(t, i))
		allpossibilities.append(alltiles[-1]['sides'])

@dataclass
class Cell:
	id:int
	pos:tuple
	neighbours:dict
	possibilities = allpossibilities
	entropy:int = len(possibilities)
	collapsed = False
	tile = None
Cell.__str__ = lambda self: f'id: {self.id}, pos: {self.pos}, neighbours: {"{...}"}, entropy: {self.entropy}, collapsed: {self.collapsed}'

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


def reduceEntropy(cell):
	ncpl = []
	n0, n1, n2, n3 = cell.neighbours.values()

	for poss in cell.possibilities:
		i = False

		# this is somehow wrong?
		for nup in n0.possibilities:
			if poss[UP] != nup[DOWN][::-1]:
				continue

			for nrp in n1.possibilities:
				if poss[RIGHT] != nrp[LEFT][::-1]:
				# if poss[RIGHT] != nrp[LEFT]:
					continue
				for ndp in n2.possibilities:
					if poss[DOWN] != ndp[UP][::-1]:
						continue
					for nlp in n3.possibilities:
						if poss[LEFT] != nlp[RIGHT][::-1]:
						# if poss[LEFT] != nlp[RIGHT]:
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

def make_image(grid, path):
	img = Image.new('RGBA', (metaconfig['DIM'] * metaconfig['TILESIZE'], metaconfig['DIM'] * metaconfig['TILESIZE']), (0, 0, 0, 0))
	for i in grid:
		for j in i:
			if j.tile:
				img.paste(j.tile['img'], (j.pos[0] * metaconfig['TILESIZE'], j.pos[1] * metaconfig['TILESIZE']))
	img.save(f'{__file__}\\..\\{path}')
	return img

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
		for tile in alltiles:
			if tile['sides'] == t:
				modifyCell.tile = tile
				break
		modifyCell.possibilities = [t]
		modifyCell.entropy = 1
		modifyCell.collapsed = True

		for i in range(metaconfig['ENTROPY_PASSES']):
			for row in grid:
				for cell in row:
					grid[cell.pos[1], cell.pos[0]] = reduceEntropy(cell)

#			print(f'Entropy pass {i} done')

		# p()


if __name__ =='__main__':
	grid = []
	for i in range(metaconfig['DIM']**2):
		grid.append(Cell(i, (i % metaconfig['DIM'], i // metaconfig['DIM']), {}))

#	2d array of size n by n
	grid = np.array(grid)
	grid = np.reshape(grid, (metaconfig['DIM'], metaconfig['DIM']))

	for row in grid:
		for cell in row:
			makeadjacencies(cell, grid)

	main_loop(grid)

	make_image(grid, 'output.png')

	p()

# todo: image reconstruction