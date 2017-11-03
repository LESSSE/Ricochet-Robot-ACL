import argparse
import sys
import itertools
import sys, os
import time

#positions in xy are from 1 to n_max
#vertices are from 0 to 

def rr_to_cnf(file_rr,file_cnf,file_aux,file_err,t):
	global n_aux
	n_aux = 0
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
			'U': 0,			'D': 1,
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
	def possible_to_prop(x1,y1,x2,y2,t):
		v1 = xy_to_v(x1,y1)
		v2 = xy_to_v(x2,y2)
		if (x1!= x2) and (y1 != y2):
			return -1 #vertice out of range
		elif v1 == v2:
			return -2 #link to same vertice
		
		if y1 == y2:
			return  n_pos + t * v_max * 2*n_max + v1 * 2*n_max + (x2 - 1) + 1
		else:
			return  n_pos + t * v_max * 2*n_max + v1 * 2*n_max + n_max + (y2 - 1) + 1
	def move_to_prop(color,direction,t):
		if direction_to_d(direction) >= 0 and color_to_k(color) >= 0 and t >= 0: 
			return  n_pos + n_poss + t * k_max * d_max + color_to_k(color) * d_max + direction_to_d(direction) + 1 
		else:
			return -1
	def aux_to_prop():
		global n_aux
		n = n_pos + n_poss + n_mov + n_aux + 1
		n_aux += 1
		return n

	lines = file_rr.readlines()
	l = lines[0].strip()

	n_max = int(l.split()[0])	#n
	v_max = n_max * n_max  		#number of vertices 
	t_max = t					#number of steps
	k_max = 4					#number of robots
	d_max = 4					#number of directions

	n_pos = (t_max+1) * v_max * k_max   			#position of each robot for each time  
	n_poss = t_max * v_max * 2*n_max				#number of possible outcomes  
	n_mov = t_max * k_max * d_max					#moves per time

	clauses = ""
	n_clauses = 0

	#initial positions__________________________
	for i in range(0,k_max):
		l = lines[i+1].strip()
		color = l.split()[0][0]
		x = int(l.split()[1])
		y = int(l.split()[2])
		clauses += str(pos_xy_to_prop(color,x,y,0))+" 0\n"
		n_clauses +=1

	#goal________________________________________
	l = lines[5].strip()
	color = l.split()[0][0]
	x = int(l.split()[1])
	y = int(l.split()[2])
	clauses += str(pos_xy_to_prop(color,x,y,t_max))+" 0\n"
	n_clauses += 1

	#map barriers_________________________________
	walls = []
	for l in lines[7:]:
		l = l.strip()
		if (l != ""):
			x1 = int(l.split()[0])
			y1 = int(l.split()[1])
			d = l.split()[2][0]
			x2,y2 = xyd_to_xy(x1,y1,d)
			v1 = xy_to_v(x1,y1)
			v2 = xy_to_v(x2,y2)
			if(v2 != -1):
				if(v2 < v1):
					v1, v2 = v2, v1
				walls += [(v1,v2)]

	edges = []
	for v in range(0,v_max):
		for d in ['R','D']:
			v2 = v
			v3 = vd_to_v(v2,d)
			while (v3 != -1) and (not (v2,v3) in walls):
				if(v != v3):
					edges += [(v,v3)]
				v2 = v3
				v3 = vd_to_v(v2,d)

	#________________________________________
	#file_err.write("\trr_to_cnf - 1. Positions: each robot have to have one position per time step\n")
	#positions
	#each robot have to have one position per time step 
	for t in range(0,t_max+1):
		for k in ['R','G','Y','B']:
			for i in range(1,n_max+1):
				for j in range(1,n_max+1):
					clauses += str(pos_xy_to_prop(k,i,j,t))+" "
			clauses += "0\n"
			n_clauses +=1

	#file_err.write("\trr_to_cnf - 2. Positions: each robot can only be at most at one position at each time step\n")
	#each robot can only be at most at one position at each time step 
	for t in range(0,t_max+1):
		for k in ['R','G','Y','B']:
			for v1 in range(0,v_max):
				for v2 in range(v1+1,v_max):
					clauses += str(-pos_v_to_prop(k,v1,t))+" "+str(-pos_v_to_prop(k,v2,t))+" 0\n"
					n_clauses +=1

	#file_err.write("\trr_to_cnf - 3. Positions: two robots can not have the same position at the same time\n")
	#each robot can only be at most at one position at each time step 
	for t in range(0,t_max+1):
		for k1 in ['R','G','Y','B']:
			for v in range(0,v_max):
				for k2 in ['R','G','Y','B']:
					if k1 != k2:
						clauses += str(-pos_v_to_prop(k1,v,t))+" "+str(-pos_v_to_prop(k2,v,t))+" 0\n"
						n_clauses +=1

	#file_err.write("\trr_to_cnf - 4. Possible: possible moves must not have robots in the middle\n")
	#possible moves must not have robots in the middle
	for t in range(0,t_max):		
		for e in edges:
			v1 = e[0]
			v2 = e[1]
			x1, y1 = v_to_x(v1),v_to_y(v1)
			x2, y2 = v_to_x(v2),v_to_y(v2)
			for v in between_xy(x1,y1,x2,y2):
				for k in ['R','G','Y','B']:
					clauses += str(-possible_to_prop(x1,y1,x2,y2,t))+" "+str(-pos_xy_to_prop(k,v[0],v[1],t)) +" 0\n"
					n_clauses += 1
			v1 = e[1]
			v2 = e[0]	
			x1, y1 = v_to_x(v1),v_to_y(v1)
			x2, y2 = v_to_x(v2),v_to_y(v2)
			for v in between_xy(x1,y1,x2,y2):
				for k in ['R','G','Y','B']:
					clauses += str(-possible_to_prop(x1,y1,x2,y2,t))+" "+str(-pos_xy_to_prop(k,v[0],v[1],t)) +" 0\n"
					n_clauses += 1

	#file_err.write("\trr_to_cnf - 5. Possible: need to have a robot at the end\n")
	#possible moves need to have a robot at the end
	for t in range(0,t_max):		
		for e in edges:
			v1 = e[0]
			v2 = e[1]
			x1, y1 = v_to_x(v1),v_to_y(v1)
			x2, y2 = v_to_x(v2),v_to_y(v2)
			d = direction_xy(x1,y1,x2,y2)
			if d != -1:
				x3, y3 = xyd_to_xy(x2,y2,d)
				if( (xy_to_v(x3,y3) != -1) and ((v1,xy_to_v(x3,y3)) in edges) ):
					s = str(-possible_to_prop(x1,y1,x2,y2,t))+" "
					for k in ['R','G','Y','B']:
						s += str(pos_xy_to_prop(k,x3,y3,t)) +" "
					s += "0\n"  
					clauses += s	
					n_clauses += 1		
			v1 = e[1]
			v2 = e[0]
			x1, y1 = v_to_x(v1),v_to_y(v1)
			x2, y2 = v_to_x(v2),v_to_y(v2)
			d = direction_xy(x1,y1,x2,y2)
			if d != -1:
				x3, y3 = xyd_to_xy(x2,y2,d)
				if( (xy_to_v(x3,y3) != -1) and ((xy_to_v(x3,y3),v1) in edges) ):
					s = str(-possible_to_prop(x1,y1,x2,y2,t))+" "
					for k in ['R','G','Y','B']:
						s += str(pos_xy_to_prop(k,x3,y3,t)) +" "
					s += "0\n"
					clauses += s  	
					n_clauses += 1

	#file_err.write("\trr_to_cnf - 6. Moves: each time step at most one robot can move\n")
	#at each time step at most one robot can move 
	for t in range(0,t_max):
		for k1 in ['R','G','Y','B']:
			for d1 in ['U','D','R','L']:
				for k2 in ['R','G','Y','B']:
					for d2 in ['U','D','R','L']:
						if k1!=k2 or d1!=d2:
							clauses += str(-move_to_prop(k1,d1,t))+" "+str(-move_to_prop(k2,d2,t))+" 0\n"
							n_clauses +=1

	#file_err.write("\trr_to_cnf - 7. Moves: for each time step each robot or stay or move\n")
	#for each time step each robot or stay or move
	for k in ['R','B','G','Y']:
		for t in range(1,t_max+1):
			for v in range(0,v_max):
				poss_mv = []
				aux_s = []
				x2, y2 = v_to_x(v),v_to_y(v)

				#get of possible movements
				for e in edges:
					if e[1] == v:
						x1, y1 = v_to_x(e[0]),v_to_y(e[0])
						d = direction_xy(x1,y1,x2,y2)
						poss_mv += [[pos_v_to_prop(k,e[0],t-1),possible_to_prop(x1,y1,x2,y2,t-1),move_to_prop(k,d,t-1)]]
					elif e[0] == v:
						x1, y1 = v_to_x(e[1]),v_to_y(e[1])
						d = direction_xy(x1,y1,x2,y2)
						poss_mv += [[pos_v_to_prop(k,e[1],t-1),possible_to_prop(x1,y1,x2,y2,t-1),move_to_prop(k,d,t-1)]]

				for i in poss_mv:
					aux = aux_to_prop()
					aux_s += [aux]
					for j in i:
						clauses += str(j)+" "+str(-aux)+" 0\n" 
						n_clauses += 1
				
				s = str(-pos_xy_to_prop(k,x2,y2,t))+" "+str(pos_xy_to_prop(k,x2,y2,t-1))+" " 

				for i in aux_s: 
					s += str(i)+" "
				
				clauses += s + " 0\n"
				n_clauses += 1
	
	n_var = n_pos + n_mov + n_poss + n_aux	#number of total propositions
	#VARS TO AUX
	vars_s = "t "+str(t_max)+"\n"
	vars_s += "n "+str(n_max)+"\n"
	vars_s += "v "+str(v_max)+"\n"
	vars_s += "k "+str(k_max)+"\n"
	vars_s += "d "+str(d_max)+"\n"
	vars_s += "V "+str(n_var)+"\n"
	file_aux.write(vars_s)

	clauses_s = "p cnf "+str(n_var)+" "+str(n_clauses)+"\n" + clauses
	file_cnf.write(clauses_s)

def cnf_to_sol(file_sol,file_cnf,file_aux,file_err,t):
	global n_aux
	global t_max

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
			 0: 'u',
			 1: 'd',
			 2: 'r',
			 3: 'l'
		}.get(d, -1)

	#TO PROP CONVERTERS		
	def prop_to_move(prop):
		if (prop >= n_pos + n_poss + 1) and (prop <= n_pos + n_poss + n_mov + 1): 
			prop -= n_pos + n_poss + 1
			time = prop // (k_max * d_max)
			robot = k_to_color((prop // d_max) % k_max)
			direction = d_to_direction(prop % d_max)
			# t * k_max * d_max + color_to_k(color) * d_max + direction_to_d(direction)
			return   (time,str(robot) +" "+str(direction)+"\n")
		else:
			return 	 (-1,-1)

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
	n_poss = t_max * v_max * 2*n_max				#number of possible outcomes  
	n_mov = t_max * k_max * d_max					#moves per time
	n_aux = n_var - (n_pos + n_mov + n_poss)

	clause = file_to_clauses(file_cnf)
	
	if(clause == -1):
		file_err.write("\tcnf_to_sol - 1. UNSATISFIABLE | t = "+str(t_max)+"\n")
		return -1

	file_err.write("\tcnf_to_sol - 1. SATISFIABLE | t = "+str(t_max)+"\n")
	#file_err.write("\tcnf_to_sol - 2. Moves: creating solution\n")
	moves = {}
	for i in clause:
			if i > 0:
				pair = prop_to_move(i)
				if pair[0] > -1:
					moves[pair[0]] = pair[1]

	file_sol.write(str(len(moves))+"\n")
	for move in sorted(moves.items()):
		file_sol.write(move[1])

	return 1

def file_to_clauses(f):
	c = []
	for l in f.readlines():
		l = l.strip()
		if (l[0] == 's'):
			if (l.split()[1] == "UNSATISFIABLE"):
				return -1
		if (l[0] == 'v'):
			nclause = map(int, l.split()[1:])
			c += list(nclause)
	return c[:-1]

def grow_function(n):
	if n < 0:
		return 0
	elif n == 0:
		return 1
	else:
		return n*2

def rr_solver(t):
		t_max = t

		#_____
		start = time.time()

		f_err = sys.stderr
		f_rr = open("problem.rr", 'r')
		f_cnf = open("problem-"+ str(t_max) +".cnf", 'w')
		f_aux = open("vars-"+ str(t_max) +".aux", 'w')
	
		#f_err.write("RR_TO_CNF | "+str(t_max)+" \n")
		rr_to_cnf(f_rr,f_cnf,f_aux,f_err,t_max)

		f_cnf.close()
		f_aux.close()


		end = time.time()

		f_err.write("RR_TO_CNF | Time: "+str(end - start)+" \n")

		#______
		start = time.time()

		#f_err.write("SAT_SOLVER\n")

		os.system("./lingeling < problem-"+str(t_max)+".cnf > solution-"+str(t_max)+".cnf")

		end = time.time()

		f_err.write("SAT_SOLVER | Time: "+str(end - start)+" \n")

		#____
		start = time.time()

		f_cnf = open("solution-"+ str(t_max) +".cnf", 'r')
		f_aux = open("vars-"+ str(t_max) +".aux", 'r')
		f_sol = open("solution-"+str(t_max)+".sol", 'w')

		#f_err.write("CNF_TO_SOL\n")
		sat = cnf_to_sol(f_sol,f_cnf,f_aux,f_err,t_max)

		end = time.time()

		f_err.write("CNF_TO_SOL | Time: "+str(end - start)+" \n")

		f_cnf.close()
		f_aux.close()

		f_err.write("______________________________________________\n")

		return sat

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Ricochet Robot Solver in SAT')
	args = parser.parse_args()

	start = time.time()

	f_problem = open("problem.rr", 'w')
	problem = sys.stdin.readlines()
	for l in problem:
		f_problem.write(l)
	f_problem.close()

	t_sat = -1 #always sat
	t_unsat = -1 #always unsat

	sat = 0

	while( sat != 1 ) and (t_sat <= 20):
		t_unsat = t_sat
		t_sat = grow_function(t_sat)
		sat = rr_solver(t_sat)
		#sys.stderr.write("GROW:: T_MAX:"+str(t_sat)+" T_MIN:"+str(t_unsat)+" SAT:"+str(sat)+"\n\n")

	sat = 0
	#sys.stderr.write("FINAL GROW:: T_MAX:"+str(t_sat)+" T_MIN:"+str(t_unsat)+" SAT:"+str(sat)+"\n\n")
	t = t_unsat + (t_sat - t_unsat) // 2
	while(t != t_unsat):
		sat = rr_solver(t)
		#sys.stderr.write("SEARCH:: T_MAX:"+str(t_sat)+" T_MIN:"+str(t_unsat)+" T:"+str(t)+" SAT:"+str(sat)+"\n\n")
		if(sat == 1):
			t_sat = t
		else:
			t_unsat = t
		t = t_unsat + (t_sat - t_unsat) // 2
		

	#sys.stderr.write("solution-"+str(t_sat)+".sol\n")
	f_solution = open("solution-"+str(t_sat)+".sol", 'r')
	solution = f_solution.readlines()
	for l in solution:
		sys.stdout.write(l)
	sys.stdout.flush()
	f_solution.close()

	end = time.time()
	sys.stderr.write("TOTAL TIME: "+str(end - start)+" \n")

	os.system("rm *.cnf *.aux problem.rr solution*.sol")
		
