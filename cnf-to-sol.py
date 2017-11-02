import argparse
import sys
import itertools

#positions in xy are from 1 to n_max
#vertices are from 0 to 

n_aux = 0 

def cnf_to_sol(file_sol,file_cnf,file_aux,file_err,t):
	global n_aux

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

	#TO PROP CONVERTERS		
	def prop_to_move(prop):
		if (prop >= n_pos + n_map + n_poss + 1) and (prop <= n_pos + n_map + n_poss + n_mov + 1): 
			prop -= n_pos + n_map + n_poss + 1
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
	n_map = (v_max-1) * (v_max) // 2				#links between two vertices on map   
	n_poss = t_max * v_max * 2*n_max				#number of possible outcomes  
	n_mov = t_max * k_max * d_max					#moves per time
	n_aux = n_var - (n_pos + n_map + n_mov + n_poss)

	clause = file_to_clauses(file_cnf)

	file_err.write("\tcnf_to_sol:1. Moves: creating solution\n")
	moves = {}
	for i in clause:
			if i > 0:
				pair = prop_to_move(i)
				if pair[0] > -1:
					moves[pair[0]] = pair[1]

	file_sol.write(str(len(moves))+"\n")
	for move in sorted(moves.items()):
		file_sol.write(move[1])

def file_to_clauses(f):
	c = []
	for l in f.readlines():
		l = l.strip()
		if (l[0] == 'v'):
			nclause = map(int, l.split()[1:])
			c += list(nclause)
	return c[:-1]

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='ricochet robots to cnf')
	parser.add_argument('-t', nargs='?', type=int, help='the number of steps', default = 1)  
	args = parser.parse_args()

	t_max = args.t

	f_err = sys.stderr
	f_cnf = open("solution-"+ str(t_max) +".cnf", 'r')
	f_aux = open("vars-"+ str(t_max) +".aux", 'r')
	f_sol = sys.stdout

	f_err.write("CNF_TO_SOL\n")
	cnf_to_sol(f_sol,f_cnf,f_aux,f_err,t_max)
	
	f_cnf.close()
	f_aux.close()
	