import argparse
import sys
import itertools
import sys, os
import time

#positions in xy are from 1 to n_max
#vertices are from 0 to 

def rr_to_smt(file_rr,file_smt,file_aux,file_err,t):
	
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

	program = ""
	program += "(declare-fun position (Int Int) (Int) )\n"
	program += "(declare-fun clear (Int Int) (Bool) )\n"
	program += "(declare-fun possible (Int Int Int) (Bool) )\n"
	program += "(declare-fun moved-robot (Int) (Int) )\n"
	program += "(declare-fun moved-dir (Int) (Int) )\n"
	#program += "(declare-fun wall (Int Int) (Bool) )\n"
	program += "(assert (forall ((t Int) (v Int)) \n\t(implies (and (>= t 0) \n\t\t(< t "+str(t_max)+") \n\t\t(>= v 0) \n\t\t(< v "+str(v_max)+") \n\t\t(clear v t)) \n\t(and (not (= v (position 0 t))) \n\t\t(not (= v (position 1 t))) \n\t\t(not (= v (position 2 t))) \n\t\t(not (= v (position 3 t)))))))"

	#initial positions__________________________
	for i in range(0,k_max):
		l = lines[i+1].strip()
		color = l.split()[0][0]
		x = int(l.split()[1])
		y = int(l.split()[2])
		v = xy_to_v(x,y)
		program += "(assert (= "+str(v)+" (position "+str(color_to_k(color))+" 0)))\n"

	#goal________________________________________
	l = lines[5].strip()
	color = l.split()[0][0]
	x = int(l.split()[1])
	y = int(l.split()[2])
	program += "(assert (= "+str(v)+" (position "+str(color_to_k(color))+" "+str(t_max)+")))\n"


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
			#	program += "(assert (wall v1 v2)))\n"
			#	program += "(assert (wall v2 v1)))\n"
				walls += [(v1,v2)]
		

	edges = []
	for v in range(0,v_max):
		for d in ['R','D']:
			v2 = v
			v3 = vd_to_v(v2,d)
			while (v3 != -1) and (not (v2,v3) in walls):
				if(v != v3):
					#program += "(assert (not (wall v v3))))\n"
					#program += "(assert (not (wall v3 v))))\n"
					edges += [(v,v3)]
				#else:
				#	program += "(assert (wall v3 v))))\n"
				#	program += "(assert (wall v v3))))\n"
				v2 = v3
				v3 = vd_to_v(v2,d)


	#________________________________________
	#file_err.write("\trr_to_smt - 1. Positions: each robot have to have one position per time step\n")
	#positions
	#each robot have to have one position per time step 
	
	program += "(assert (forall ((t Int) (k Int) (v Int)) \n\t(implies \n\t\t(and (>= t 0) \n\t\t\t(< t "+str(t_max+1)+") \n\t\t\t(>= k 0) \n\t\t\t(< k "+str(k_max)+") \n\t\t\t(= v (position k t))) \n\t\t(and \n\t\t\t(>= v 0) \n\t\t\t(< v "+str(v_max)+" )))))\n"
	
	#file_err.write("\trr_to_smt - 2. Positions: two robots can not have the same position at the same time\n")
	#each robot can only be at most at one position at each time step 
	
	program += "(assert (forall ((t Int) (k1 Int) (k2 Int) (v1 Int) (v2 Int)) \n\t(implies \n\t\t(and (>= t 0) \n\t\t\t(< t "+str(t_max+1)+") \n\t\t\t(>= k1 0) \n\t\t\t(< k1 "+str(k_max)+") \n\t\t\t(>= k2 0) \n\t\t\t(< k2 "+str(k_max)+") \n\t\t\t(not (= k1 k2)) \n\t\t\t(= v1 (position k1 t)) \n\t\t\t(= v2 (position k2 t))) \n\t\t(not (= v1 v2)))))\n"
		
	#file_err.write("\trr_to_smt - 3. Possible: possible moves must not have robots in the middle and must have one at the end\n")
	#possible moves must not have robots in the 
		
	for e in edges:
		v1 = e[0]
		v2 = e[1]
		program += "(assert (forall ((t Int)) \n\t(implies \n\t\t(and (>= t 0) \n\t\t\t(< t "+str(t_max)+") \n\t\t\t(possible "+str(v1)+" "+str(v2)+" t)) \n\t\t(and "
		x1, y1 = v_to_x(v1),v_to_y(v1)
		x2, y2 = v_to_x(v2),v_to_y(v2)
		for v in between_xy(x1,y1,x2,y2):
			ve = xy_to_v(v[0],v[1])
			program += "\n\t\t\t(clear "+str(ve)+" t)"
		d = direction_xy(x1,y1,x2,y2)
		if d != -1:
			x3, y3 = xyd_to_xy(x2,y2,d)
			if( (xy_to_v(x3,y3) != -1) and ((v1,xy_to_v(x3,y3)) in edges) ):
				v3 = xy_to_v(x3,y3)
				program += "\n\t\t\t(not (clear "+str(v3)+" t))"
		program += "))))\n"
		v1 = e[1]
		v2 = e[0]	
		x1, y1 = v_to_x(v1),v_to_y(v1)
		x2, y2 = v_to_x(v2),v_to_y(v2)
		program += "(assert (forall ((t Int)) \n\t(implies \n\t\t(and (>= t 0) \n\t\t\t(< t "+str(t_max)+") \n\t\t\t(possible "+str(v1)+" "+str(v2)+" t)) \n\t\t(and "
		for v in between_xy(x1,y1,x2,y2):
			ve = xy_to_v(v[0],v[1])
			program += "\n\t\t\t(clear "+str(ve)+" t)"
		d = direction_xy(x1,y1,x2,y2)
		if d != -1:
			x3, y3 = xyd_to_xy(x2,y2,d)
			if( (xy_to_v(x3,y3) != -1) and ((v1,xy_to_v(x3,y3)) in edges) ):
				v3 = xy_to_v(x3,y3)
				program += "\n\t\t\t(not (clear "+str(v3)+" t))"
		program += "))))\n"		

	#file_err.write("\trr_to_smt - 4. Moves: for each time step each robot or stay or move\n")
	#for each time step each robot or stay or move
	for v in range(0,v_max):
		poss_mv = []
		aux_s = []
		x2, y2 = v_to_x(v),v_to_y(v)
		program += "(assert (forall ((t Int) (k Int)) \n\t(implies \n\t\t(and (>= t 1) \n\t\t\t(< t "+str(t_max+1)+") \n\t\t\t(>= k 0) \n\t\t\t(< k "+str(k_max+1)+") \n\t\t\t(= (position k t) "+str(v)+")) \n\t\t(or "
		program += "(= (position k (- t 1)) "+str(v)+"))"
	
		for e in edges:
			if e[1] == v:
				x1, y1 = v_to_x(e[0]),v_to_y(e[0])
				d = direction_to_d(direction_xy(x1,y1,x2,y2))
				program += "\n\t\t\t(and \n\t\t\t\t(= (position k (- t 1)) "+str(e[0])+") \n\t\t\t\t(possible "+str(e[0])+" "+str(v)+" (- t 1)) \n\t\t\t\t(= (moved-robot (- t 1)) k) \n\t\t\t\t(= (moved-dir (- t 1)) "+str(d)+"))"
				
			elif e[0] == v:
				x1, y1 = v_to_x(e[1]),v_to_y(e[1])
				d = direction_to_d(direction_xy(x1,y1,x2,y2))
                                program += "\n\t\t\t(and \n\t\t\t\t(= (position k (- t 1)) "+str(e[1])+") \n\t\t\t\t(possible "+str(e[1])+" "+str(v)+" (- t 1)) \n\t\t\t\t(= (moved-robot (- t 1)) k) \n\t\t\t\t(= (moved-dir (- t 1)) "+str(d)+"))"
		
		program += ")))\n"

	n_var = n_pos + n_mov + n_poss	#number of total propositions
	#VARS TO AUX
	vars_s = "t "+str(t_max)+"\n"
	vars_s += "n "+str(n_max)+"\n"
	vars_s += "v "+str(v_max)+"\n"
	vars_s += "k "+str(k_max)+"\n"
	vars_s += "d "+str(d_max)+"\n"
	vars_s += "V "+str(n_var)+"\n"
	file_aux.write(vars_s)

	program += "(check-sat)"
	file_smt.write(program)

def smt_to_sol(file_sol,file_smt,file_aux,file_err,t):
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

	clause = file_to_clauses(file_smt)
	
	if(clause == -1):
		file_err.write("\tsmt_to_sol - 1. UNSATISFIABLE | t = "+str(t_max)+"\n")
		return -1

	file_err.write("\tsmt_to_sol - 1. SATISFIABLE | t = "+str(t_max)+"\n")
	#file_err.write("\tsmt_to_sol - 2. Moves: creating solution\n")
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
		f_smt = open("problem-"+ str(t_max) +".smt", 'w')
		f_aux = open("vars-"+ str(t_max) +".aux", 'w')
	
		#f_err.write("RR_TO_smt | "+str(t_max)+" \n")
		sys.stderr.write("Timesteps: "+str(t_max)+"\n")
		rr_to_smt(f_rr,f_smt,f_aux,f_err,t_max)

		f_smt.close()
		f_aux.close()


		end = time.time()

		f_err.write("RR_TO_smt | Time: "+str(end - start)+" \n")


		#______
		start = time.time()

		#f_err.write("SAT_SOLVER\n")

		os.system("./../z3-4.5.0-x64-ubuntu-14.04/bin/z3 -smt2 problem-"+str(t_max)+".smt > solution-"+str(t_max)+".smt")

		end = time.time()

		f_err.write("SAT_SOLVER | Time: "+str(end - start)+" \n")

		'''
		#____
		start = time.time()

		f_smt = open("solution-"+ str(t_max) +".smt", 'r')
		f_aux = open("vars-"+ str(t_max) +".aux", 'r')
		f_sol = open("solution-"+str(t_max)+".sol", 'w')

		#f_err.write("smt_TO_SOL\n")
		sat = smt_to_sol(f_sol,f_smt,f_aux,f_err,t_max)

		end = time.time()

		f_err.write("smt_TO_SOL | Time: "+str(end - start)+" \n")

		f_smt.close()
		f_aux.close()

		f_err.write("______________________________________________\n")
		'''
		return -1

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

	os.system("rm *.smt *.aux problem.rr solution*.sol")
		
