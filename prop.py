def calc(vars):
	global n_max
	global v_max
	global t_max
	global k_max
	global d_max
	global n_var
	global n_pos
	global n_map
	global n_poss
	global n_mov
	global n_aux

	file_aux = open("vars-"+str(vars)+".aux", 'r')
	lines = file_aux.readlines()

	for l in lines:
		l1 = l.strip().split()
		if l1[0]=='n':
			n_max = int(l1[1])	#n
		elif l1[0]=='v':
			v_max = int(l1[1])  #number of vertices 
		elif l1[0]=='t':
			t_max = int(l1[1])	#number of steps
		elif l1[0]=='k':
			k_max = int(l1[1])	#number of robots
		elif l1[0]=='d':
			d_max = int(l1[1])	#number of directions
		elif l1[0]=='V':
			n_var = int(l1[1])	#number of total propositions
		else:
			exit

	n_pos = (t_max+1) * v_max * k_max   			#position of each robot for each time                      	
	n_map = (v_max-1) * (v_max) // 2				#links between two vertices on map   
	n_poss = t_max * v_max * 2*n_max				#number of possible outcomes  
	n_mov = t_max * k_max * d_max					#moves per time
	n_aux = n_var - (n_pos + n_map + n_mov + n_poss)


def xy_to_v(x,y): 
	'''
	gives the vertice correpondent to (x,y)
	Input: x,y between 1 and n_max
	Output: vertice between 0 and n_max^2-1
	Error: -1 if x,y out of range
	'''
	if (x in range(1,n_max+1)) and (y in range(1,n_max+1)): 
		return (x-1) * n_max + (y-1)
	else:
		return -1	
def color_to_k(color):
	'''
	gives a numerical code for color
	Input: character with color
	Output: 0,1,2,3
	Error: -1 when color not designated
	'''
	return{
		'R': 0,
		'G': 1,
		'Y': 2,
		'B': 3
	}.get(color, -1)
def direction_to_d(direction):
	'''
	gives a numerical code for direction
	Input: character with direction
	Output: 0,1,2,3
	Error: -1 when direction not designated
	'''
	return {
		'U': 0,
		'D': 1,
		'R': 2,
		'L': 3
	}.get(direction.upper(), (-1,-1))
def xyd_to_xy(x,y,direction):
	'''
	gives the next pair of coordinates in folowing
	Input: pair of coordinates and direction
	Output: pair of coordinates between 1 and n_max
	Error: (-1,-1) when direction not designated or when old or new (x1,y1) out of range
	'''
	x2, y2 = {
		'U':(x-1,y),
		'D':(x+1,y),
		'R':(x,y+1),
		'L':(x,y-1)
	}.get(direction.upper(), (-1,-1))
	if x2 in range(1,n_max+1) and y2 in range(1, n_max+1):
		return (x2,y2)
	else:
		return (-1,-1)
def vd_to_v(v,direction):
	'''
	gives the next vertice folowing direction
	Input: vertice and direction
	Output:  vertice between n and n_max^2-1
	Error: -1 when direction not designated or when old or new v out of range
	'''	
	if not v in range(0,v_max):
		return -1 
	elif v%n_max == 0 and direction == 'L':
		return -1
	elif v%n_max == n_max-1 and direction == 'R':
		return -1
	elif v >= n_max*(n_max-1) and direction == 'D':
		return -1
	elif v < n_max  and direction == 'U':
		return -1
	else:
		return{
			'U':v-n_max,
			'D':v+n_max,
			'R':v+1,
			'L':v-1,
		}.get(direction.upper(), -1)
def v_to_x(v):
	if v in range(0,v_max): 
		return v // n_max +1
	else:
		return -1	
def v_to_y(v):
	if v in range(0,v_max): 
		return v % n_max + 1
	else:
		return -1	
def between_xy(x1,y1,x2,y2):
	between = []
	if (not ((x1 == x2) or (y1 == y2))) or (not ((x1 in range(1,n_max+1)) and (y1 in range(1,n_max+1)) and (x2 in range(1,n_max+1)) and (y2 in range(1,n_max+1)))): 
		between = []
	elif (x1 == x2):
		if (y2 < y1):
			for i in range(y2,y1):
				between += [(x1,i)]
		else:
			for i in range(y1+1,y2+1):
				between += [(x1,i)]
	else:
		if (x2 < x1):
			for i in range(x2,x1):
				between += [(i,y1)]
		else:
			for i in range(x1+1,x2+1):
				between += [(i,y1)]
	return between
def direction_xy(x1,y1,x2,y2):
	if ((x1 != x2) and (y1 != y2)) or (not ((x1 in range(1,n_max+1)) and (y1 in range(1,n_max+1)) and (x2 in range(1,n_max+1)) and (y2 in range(1,n_max+1)))): 
		d = -1
	elif (x1 == x2):
		if (y2 < y1):
			d = 'L'
		else:
			d = 'R'
	else:
		if (x2 < x1):
			d = 'U'
		else:
			d = 'D'
	return d

#TO PROP CONVERTERS		
def pos_xy_to_prop(color,x,y,t):
	'''
	gives the number of the proposition that corresponds to robot of *color* beeing at position (*x*,*y*) at timestep *t*
	Input: color: char ['B','Y','G',R'], x: int [1, n_max], y: int [1, n_max], t: int [0, t_max]
	Output: number of proposition 
	Error: -1 when wrong arguments
	'''
	if xy_to_v(x,y) >= 0 and color_to_k(color) >= 0 and t >= 0: 
		return  t * k_max * v_max + color_to_k(color) * v_max + xy_to_v(x,y) + 1
	else:
		return -1
def pos_v_to_prop(color,v,t):
	'''
	gives the number of the proposition that corresponds to robot of *color* beeing at vertice *v* at timestep *t*
	Input: color: char ['B','Y','G',R'], x: int [1, n_max], y: int [1, n_max], t: int [0, t_max]
	Output: number of proposition 
	Error: -1 when wrong arguments
	'''
	if v >= 0 and color_to_k(color) >= 0 and t >= 0: 
		return   t * k_max * v_max + color_to_k(color) * v_max + v + 1
	else:
		return -1
def link_to_prop_xy(x1,y1,x2,y2):
	'''
	gives the number of the proposition that corresponds to the link between the position (*x1*,*y1*) and position (*x2*,y2*)
	Input: x1: int [1, n_max], y1: int [1, n_max], x2: int [1, n_max], y2: int [1, n_max]
	Output: number of proposition 
	Error: -1 when wrong arguments; -2 when the vertice is the same
	'''
	v1 = xy_to_v(x1,y1)+1;
	v2 = xy_to_v(x2,y2)+1;
	if v1 <= 0 or v2 <= 0:
		return -1 #vertice out of range
	elif v1 == v2:
		return -2 #link to same vertice
	elif v2 < v1:
		v1, v2 = v2, v1
	return n_pos + (v2-v1) + (v_max-v2) * (v_max-v2+1)//2 + 1
def link_to_prop_v(v1,v2):
	'''
	gives the number of the proposition that corresponds to the link between the position (*x1*,*y1*) and position (*x2*,y2*)
	Input: x1: int [1, n_max], y1: int [1, n_max], x2: int [1, n_max], y2: int [1, n_max]
	Output: number of proposition 
	Error: -1 when wrong arguments; -2 when the vertice is the same
	'''
	if v1 <= 0 or v2 <= 0:
		return -1 #vertice out of range
	elif v1 == v2:
		return -2 #link to same vertice
	elif v2 < v1:
		v1, v2 = v2, v1
	return n_pos + (v2-v1) + (v_max-v2) * (v_max-v2+1)//2 + 1
def possible_to_prop(x1,y1,x2,y2,t):
	v1 = xy_to_v(x1,y1)
	v2 = xy_to_v(x2,y2)
	if (x1!= x2) and (y1 != y2):
		return -1 #vertice out of range
	elif v1 == v2:
		return -2 #link to same vertice
	
	if y1 == y2:
		return  n_pos + n_map + t * v_max * 2*n_max + v1 * 2*n_max + x2 + 1
	else:
		return  n_pos + n_map + t * v_max * 2*n_max + v1 * 2*n_max + n_max * y2 + 1
def move_to_prop(color,direction,t):
	if direction_to_d(direction) >= 0 and color_to_k(color) >= 0 and t >= 0: 
		return  n_pos + n_map + n_poss + t * k_max * d_max + color_to_k(color) * d_max + direction_to_d(direction) + 1 
	else:
		return -1
def aux_to_prop():
	global n_aux
	n = n_pos + n_map + n_poss + n_mov + n_aux + 1
	n_aux += 1
	return n

def k_to_color(k):
	'''
	gives a numerical code for color
	Input: character with color
	Output: 0,1,2,3
	Error: -1 when color not designated
	'''
	return{
		 0: 'R',
		 1: 'G',
		 2: 'Y',
		 3: 'B'
	}.get(k, -1)
def d_to_direction(d):
	'''
	gives a numerical code for direction
	Input: character with direction
	Output: 0,1,2,3
	Error: -1 when direction not designated
	'''
	return {
		 0: 'U',
		 1: 'D',
		 2: 'R',
		 3: 'L'
	}.get(d, -1)

def prop_to_move(prop):
	if (prop >= n_pos + n_map + n_poss + 1) and (prop <= n_pos + n_map + n_poss + n_mov + 1): 
		prop -= n_pos + n_map + n_poss + 1
		time = prop // (k_max * d_max)
		robot = k_to_color((prop // d_max) % k_max)
		direction = d_to_direction(prop % d_max)
		# t * k_max * d_max + color_to_k(color) * d_max + direction_to_d(direction)
		return   ("MOVE: t: "+str(time)+" k: "+str(robot)+" d: "+str(direction)+"\n")
	else:
		return 	 -1
def prop_to_pos(prop):
	if (prop >= 1) and (prop <= n_pos + 1): 
		prop -= 1
		time = prop // (k_max * v_max)
		robot = k_to_color((prop // v_max) % k_max)
		v = prop % v_max
		return   ("POSITION: t: "+str(time)+" k: "+str(robot)+" (x,y): ("+str(v_to_x(v))+","+str(v_to_y(v))+")\n")
	else:
		return 	 -1

def prop_to_aux(prop):
	if (prop >= n_pos + n_map + n_mov + n_poss): 
		return   ("AUX:")
	else:
		return 	 -1

def prop_to_poss(prop):
	if (prop >= n_pos + n_map + 1) and (prop <=  n_pos + n_poss + 1): 
		prop -= n_pos + n_map + 1
		time = prop // (v_max * 2*n_max )
		v1 = (prop // 2*n_max) % v_max
		v2 = (prop % 2*n_max)
		if( v2 > n_max):
			v2 -= n_max
		#  t * v_max * 2*n_max + v1 * 2*n_max + x2 + 1
		return   ("POSSIBLE: t: "+str(time)+" (x1,y1): ("+str(v_to_x(v1))+","+str(v_to_y(v1))+" (x2,y2): ("+str(v_to_x(v2))+","+str(v_to_y(v2))+"\n")
	else:
		return 	 -1

def prop_to_text(prop):
	s = prop_to_pos(prop)
	if ( s != -1 ):
		return s
	s = prop_to_move(prop)
	if ( s != -1 ):
		return s
	s = prop_to_poss(prop)
	if ( s != -1 ):
		return s
	s = prop_to_aux(prop)
	if ( s != -1 ):
		return s