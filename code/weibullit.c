/* $Id: weibullit.c,v 1.35 2005/01/21 10:45:21 schaefer Exp $ */

/*
 * weibullit.c
 * this programm reads a miluph input file and distributes flaws
 * according to the weibull distribution which describes fatigue of
 * material
 * see Benz' and Asphaug's model, described in
 * Simulations of brittle solids using smooth particle
 * hydrodynamics, Comp. Phys. Comm. 87 (1995) 253-265
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <getopt.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>


#define PROGRAM "weibullit"
#define VERSION "0.03-a"

#define TRUE 1
#define FALSE 0


#define DIM 3
#define MAXFLAWS 40



void read_particles(FILE *);
void weibullit(double, double, int, double);

struct Particle {
	double 		x[DIM];
	double 		v[DIM];
	double 		m;
	double 		rho;
	double 		e;
	double 		hsml;
	int 		noi;
	int 		material_type;
	double 		damage;
	double 		S[DIM][DIM];
	double 		temperature;
	double 		plastic_strain;
    double      p;
    double      alpha;
	struct {
			int nof;
			double *activation_threshold;
	} flaws;
} *p;
		

int verbose = FALSE;
int restarted_run = FALSE;
int porous = FALSE;
int number = 0;
int wb_number = 0;
int plastic_strain_flag = FALSE;

int material_type = -2;

static void usage(char *name) 
{
	fprintf(stderr, "Usage %s [options]\n"
			" program to weibull a miluph input file.\n"	       
			"Available options (SI units):\n"
			"\t-h, --help\t\t This message.\n"
			"\t-V, --version\t\t Version number and program name.\n"
			"\t-v, --verbose\t\t Verbose mode on (default: off).\n"
			"\t-n, --number\t\t Number of input lines (particles) (default: 0).\n"
			"\t-k, --constant_k\t Value for the Weibull constant k (default: 0).\n"
			"\t-m, --constant_m\t Value for the Weibull constant m (default: 0).\n"
			"\t-B, --basalt\t\t Macro option, predefined values for k, m for basalt.\n"
			"\t-t, --material_type\t Only weibull particles with material type material_type (default: all)\n"
            "\t-P, --porous\t\t Input file is for POROUS_JUTZI (default: FALSE).\n"
			"\t-S, --plastic_strain_flag\t\t Input file is with MISES_plasticity or JC_Plasticity (defaul: FALSE).\n"
			"\t-s, --seed\t\t Seed for the rand() function. (default: 1)\n"
			"\t-M, --max\t\t Maximum number of flaws per particle (default: none).\n"
			"\t-A, --volume\t\t Target volume (default: calculated from particles' masses and densities).\n"
			"\t-f, --filename\t\t Input file name (default: stdin).\n"
			"\t-o, --output\t\t Output file name (default: stdout).\n"
			"\t-e, --sph98\t\t Output file format is input for sph98_2.0.\n"
			"\t-p, --parasph\t\t Output file format is input parasph_2.0.\n"
			, name);
	exit(0);
}

	
void InitializeParticleArray()
{
  int i, j, k;

  for (i=0; i<number; i++) {
      for (j=0; j<DIM; j++) {
          p[i].x[j] = 0.0;
          p[i].v[j] = 0.0;
          for (k=0; k<DIM; k++) {
              p[i].S[j][k] = 0.0;
          }
      }
      p[i].m 			= 0.0;
      p[i].rho 			= 0.0;
      p[i].e 			= 0.0;
      p[i].hsml 		= 0.0;
      p[i].noi 			= 0;
      p[i].material_type= 0;
      p[i].damage 		= 0.0;

      p[i].flaws.nof	= 0;
      p[i].flaws.activation_threshold = NULL;
  }
}


int main(int argc, char *argv[])
{
	int i, c;
	int d, e;
	int sph98;
	int parasph;
	int basalt;
	unsigned int seed;
	double k, m;
	char filename[256];
	char outputname[256];
	int maxflaws = 1000000;
	double volume = -1.0;

	FILE *in, *out;

	static struct option opts[] = {
		{ "help", 0, NULL, 'h' },
		{ "version", 0, NULL, 'V' },
		{ "verbose", 0, NULL, 'v' },
		{ "filename", 0, NULL, 'f' },
		{ "number", 1, NULL, 'n' },
		{ "restarted", 0, NULL, 'r' },
		{ "basalt", 0, NULL, 'B' },
		{ "volume", 0, NULL, 'A' },
		{ "max", 1, NULL, 'M' },
		{ "porous", 0, NULL, 'P' },
		{ "plastic_strain_flag", 0, NULL, 'S' },
		{ "sph98", 0, NULL, 'e' },
		{ "parasph", 0, NULL, 'p' },
		{ "output", 1, NULL, 'o' },
		{ "seed", 1, NULL, 's' },
		{ "material_type", 1, NULL, 't' },
		{ "constant_k", 1, NULL, 'k' },
		{ "constant_m", 1, NULL, 'm' }
	};

	k = m = 0;
	outputname[0] = '\0';
	filename[0] = '\0';
	seed = 1;
	basalt = FALSE;
	sph98 = FALSE;
	parasph = FALSE;
    porous = FALSE;
	plastic_strain_flag = FALSE;

	if (argc == 1)
		usage(argv[0]);

	while ((c = (getopt_long(argc, argv, "PpeBSs:A:M:t:o:m:k:f:n:rhVv", opts, &i))) != -1) {
		switch (c) {
            case 'P':
                porous = TRUE;
                break;
			case 'S':
				plastic_strain_flag = TRUE;
				break;
			case 'A': 
				volume = atof(optarg);
				if (volume < 0) {
					fprintf(stderr, "err. volume < 0\n");
					exit(1);
				}
				break;
			case 'M':
				maxflaws = atoi(optarg);
				if (maxflaws < 1) {
					fprintf(stderr, "Err? Maxflaws should be at least 1.\n");
					exit(1);
				}
                break;
			case 'p':
				parasph = TRUE;
				break;			
			break;
			case 'h':
				usage(argv[0]);
                break;
			case 'V':
				fprintf(stderr, "This is " PROGRAM " version " VERSION ".\n");
				exit(0);	
			case 'v':
				fprintf(stderr, "Verbose mode on.\n");
				verbose = TRUE;
				break;
			case 'B':
				basalt = TRUE;
				break;
			case 'e':
				sph98 = TRUE;
				break;
			case 't':
				material_type = atoi(optarg);
				fprintf(stderr, "Only weibulling particles with material type %d\n", material_type);
				break;
			case 'n':
				number = atoi(optarg);
				if (number < 0) {
					fprintf(stderr, "Err? Number of particles less than zero.\n");
					exit(1);
				}
				break;
			case 'f':
				strcpy(filename, optarg);
				break;
			case 'k':
				k = atof(optarg);
				if (k < 0) {
					fprintf(stderr, "Err? k is less than zero.\n");
					exit(1);
				}
				break;
			case 'm':
				m = atof(optarg);
				if (m < 0) {
					fprintf(stderr, "Err? m is less than zero.\n");
					exit(1);
				}
				break;
			case 's':
				seed = atoi(optarg);
				if (seed < 1) {
					fprintf(stderr, "Err. Seed should be more than zero.\n");
					exit(1);
				}
				break;
			case 'r':
				restarted_run = TRUE;
				break;
			case 'o':
				strcpy(outputname, optarg);
				break;
		}

	}

	if (parasph && sph98) {
		fprintf(stderr, "Err. Cannot write in both sph98 and parasph "
				"file formats. Life needs decisions.\n");
		exit(1);
	}

	if (!filename[0]) {
		in = stdin;
//		fprintf(stderr, "Err. Do not know which file to open.\n");
//		exit(1);
	}

	if (verbose) {
		fprintf(stderr, "Number of particles: %d\n", number);
		fprintf(stderr, "Opening file: %s\n", filename);
		fprintf(stderr, "Constant k for the Weibull distribution: %e\n", k);
		fprintf(stderr, "Constant m for the Weibull distribution: %e\n", m);
		fprintf(stderr, "Setting seed of rand() function to: %d\n", seed);
	}

	srand(seed);

	/* allocate mem */
	if (!(p = malloc(sizeof(struct Particle) * number))) {
		fprintf(stderr, "Err. Buy more mem.\n");
		exit(1);
	} else if (verbose) {
		fprintf(stderr, "%d particles allocated.\n", number);
	}

	if (filename[0] && ((in = fopen(filename, "r")) == NULL)) {
		fprintf(stderr, "Err. Cannot open %s\n", filename);
		exit(1);
	} else {
		read_particles(in);
		fclose(in);	
	}


	if (basalt) {
		m = 8.5;
		k = 5.0e34;
		if (verbose) {
			fprintf(stderr, "Setting predefined values: \n");
			fprintf(stderr, "k: %le 1/m**3\n", k);
			fprintf(stderr, "m: %le\n", m);
		}
	}

	/* if only special particles have to be weibulled, we need to
	 * count 'em */
	if (material_type > -1) {
		for (i = 0; i < number; i++) {
			if (p[i].material_type == material_type)
				wb_number++;
		}
	} else 
		wb_number = number;

	fprintf(stderr, "Weibulling %d particles\n", wb_number);
	
	/* now weibull it! */
	weibullit(k, m, maxflaws, volume);

	/* now print out what we have done */
	if (outputname[0]) {
		if (!(out = fopen(outputname, "w"))) {
			fprintf(stderr, "Err. Cannot write to %s.\n", outputname); 
			exit(1);
		}
	} else {
		out = stdout;
	}

	if (!sph98 && !parasph) {
		for (i = 0; i < number; i++) {
			for (d = 0; d < DIM; d++) 
				fprintf(out, "%le\t", p[i].x[d]);
			for (d = 0; d < DIM; d++) 
				fprintf(out, "%le\t", p[i].v[d]);
			fprintf(out, "%le\t", p[i].m);
			fprintf(out, "%.10e\t", p[i].rho);
			fprintf(out, "%le\t", p[i].e);
			if (restarted_run) {
				fprintf(out, "%le\t", p[i].hsml);
				fprintf(out, "%d\t", p[i].noi);
			}
			fprintf(out, "%d\t", p[i].material_type);
			fprintf(out, "%d\t", p[i].flaws.nof);
			fprintf(out, "%le\t", p[i].damage);
			if (plastic_strain_flag) {
				fprintf(out, "%le\t", p[i].plastic_strain);
				fprintf(out, "%le\t", p[i].temperature);
			}	
			for (d = 0; d < DIM; d++) 
				for (e = 0; e < DIM; e++)
					fprintf(out, "%le\t", p[i].S[d][e]);
			/* and now the flaws */
            if (porous) {
                fprintf(out, "%le\t", p[i].alpha);
                fprintf(out, "%le\t", p[i].p);
            }
			for (d = 0; d < p[i].flaws.nof; d++) 
				fprintf(out, "%le\t", p[i].flaws.activation_threshold[d]);
			fprintf(out, "\n");
		}	
	} else if (sph98) { /* sph98 input file */
		for (i = 0; i < number; i++) {
			fprintf(out, "%d\t", i);
			fprintf(out, "%e\t", p[i].m);
			fprintf(out, "%d\t", p[i].material_type);
			fprintf(out, "%d\t", p[i].flaws.nof);
			assert(p[i].flaws.nof <= 40);
			for (d = 0; d < p[i].flaws.nof; d++) {
				fprintf(out, "%e\t", p[i].flaws.activation_threshold[d]);
			}
			for (d = p[i].flaws.nof; d < 40; d++) {
				fprintf(out, "%e\t", -1.0);
			}
			for (d = 0; d < DIM; d++) 	
				fprintf(out, "%e\t", p[i].x[d]);
			for (d = 0; d < DIM; d++) 
				fprintf(out, "%e\t", p[i].v[d]);
			fprintf(out, "%e\t", p[i].rho);
			for (d = 0; d < DIM; d++) 
				for (e = 0; e < DIM; e++)
					fprintf(out, "%e\t", p[i].S[d][e]);
			fprintf(out, "%le\t", p[i].damage);
			fprintf(out, "\n");
		}
	} else if (parasph) { /* parasph input file */
		for (i = 0; i < number; i++) {
			for (d = 0; d < DIM; d++) 
				fprintf(out, "%le\t", p[i].x[d]);
			for (d = 0; d < DIM; d++) 
				fprintf(out, "%le\t", p[i].v[d]);
			fprintf(out, "%le\t", p[i].m);
			fprintf(out, "%le\t", p[i].rho);
			fprintf(out, "%le\t", p[i].e);
			fprintf(out, "%le\t", (double) p[i].material_type);
			fprintf(out, "%le\t", p[i].damage);
			for (d = 0; d < DIM; d++) 
				for (e = 0; e < DIM; e++)
					fprintf(out, "%le\t", p[i].S[d][e]);
			fprintf(out, "%le\t", (double) p[i].flaws.nof);
			/* and now the flaws */
			for (d = 0; d < p[i].flaws.nof; d++) 
				fprintf(out, "%le\t", p[i].flaws.activation_threshold[d]);
			for (d = p[i].flaws.nof; d < MAXFLAWS; d++) 
				fprintf(out, "-1.0\t");
			fprintf(out, "\n");
		}
	}
	
	/* free memory */
	free(p);
	/* jo! Done. */
	if (verbose)
		fprintf(stderr, "Done.\n");
	return 0;
}


void read_particles(FILE *in)
{
	int d, e;
	int i;
	struct Particle *tmp;
	
	tmp = p;

	if (verbose) 
		fprintf(stderr, "Reading particles....\n");
		
	for (i = 0; i < number; i++, p++) {
		for (d = 0; d < DIM; d++) 
			fscanf(in, "%le", &p->x[d]);
		for (d = 0; d < DIM; d++)
			fscanf(in, "%le", &p->v[d]);
		fscanf(in, "%le", &p->m);
		fscanf(in, "%le", &p->rho);
		fscanf(in, "%le", &p->e);
		if (restarted_run) {
			fscanf(in, "%le", &p->hsml);
			fscanf(in, "%d", &p->noi);
		}
		fscanf(in, "%d", &p->material_type);
		fscanf(in, "%d", &p->flaws.nof);
		fscanf(in, "%le", &p->damage);
		if (plastic_strain_flag) {
			fscanf(in, "%le", &p->plastic_strain);
			fscanf(in, "%le", &p->temperature);
		}
		for (d = 0; d < DIM; d++) 
			for (e = 0; e < DIM; e++)
				fscanf(in, "%le", &p->S[d][e]);
    	if (porous) {
			fscanf(in, "%le", &p->alpha);
            fscanf(in, "%le", &p->p);
        }

		/* 
		 * if this is a restarted run, the input file contains
		 * information about the flaws 
		 * read it and forget it
		 */
		if (restarted_run) {
			fprintf(stderr, "You do not want to do this. Look at the src.\n");
			exit(1);
			/* allocate mem for the flaws */
			if (!(p->flaws.activation_threshold = malloc(sizeof(double) * p->flaws.nof))) {
				fprintf(stderr, "Cannot allocate enough memory for the flaws.\n");
				exit(1);
			}
			/* read in flaws */
			for (d = 0; d < p->flaws.nof; d++) {
				fscanf(in, "%le", &p->flaws.activation_threshold[d]);
			}
		}
	}

	if (verbose)
		fprintf(stderr, "Particles read.\n");
	p = tmp;
}



void weibullit(double k, double m, int maxflaws, double volume)
{
	int i, j;
	int n_f;
	int d;
	int imiss, imiss_start;
    int *indices;
    int cnt = 0;
    int ii;
	int random_particle_id;
	double vol;
	double activation_threshold;
	float tmp;
	struct Particle **missing;

	if (verbose)
	    fprintf(stderr, "Now weibulling the particles.\n");

	/* number of crack activation threshold strains */
	tmp = wb_number * log((double)wb_number);
	n_f = (int) tmp;
	if (verbose)
	    fprintf(stderr, "Distributing %d crack activation threshold strains for %d particles.\n", n_f, wb_number);
	if (volume < 0) {
		volume = 0.0;
		for (i = 0; i < number; i++) {
			p[i].flaws.nof = 0;
			/* calc target volume */
			if (material_type < 0) {
				vol = p[i].m/p[i].rho;
            } else {
			    if (p[i].material_type == material_type)
			        vol = p[i].m/p[i].rho;
			}
            if (porous) {
                vol /= p[i].alpha;
            }
            volume += vol;
		}
		            fprintf(stderr, "vol %e alpha %e\n", vol, p[i].alpha);
	}
	fprintf(stderr, "Target volume: %e\n", volume);
	for (i = 0; i < n_f; i++) {
		/* randomly choose a particle between 0 and number */	

random1:
		random_particle_id = 0 + (int) ((float) number * rand()/(RAND_MAX + 1.0));
		j = random_particle_id;
		/* check if particle has already enough flaws */
		if (p[j].flaws.nof >= maxflaws) {
			goto random1;
		}
		/* check if the particle has the wrong material_type */
		if (material_type > -1) {
			if (p[j].material_type != material_type)
				goto random1;
		}
		/* 
		 * activation threshold derived from the weibull
		 * distribution 
		 */
		activation_threshold = pow((i+1)/(k*volume), 1./m);
		/* allocate mem for the flaw */
		d = p[j].flaws.nof;
		if (!(p[j].flaws.activation_threshold = realloc(p[j].flaws.activation_threshold, sizeof(double) * (d+1)))) {
				fprintf(stderr, "Cannot allocate enough mem for flaws.\n");
				exit(1);
		}
		p[j].flaws.activation_threshold[d] = activation_threshold;
		p[j].flaws.nof++;
	}

	/* 
	 * now, number * ln(number) flaws are distributed, but we want
	 * each particle to have at least one flaw. So let's look for
	 * the ones without flaws
	 */
	if (verbose)
	    fprintf(stderr, "Making sure each particle gets at least one flaw...\n");
	imiss = 0;
	if (!(indices = malloc(sizeof(int)*number)))  {
		fprintf(stderr, "Error: cannot allocate memory for missing indices list.\n");
		exit(1);
	}
	for (i = 0; i < number; i++) {
		/* check if the particle has the right material_type */
		if (material_type > -1 && p[i].material_type != material_type)
			continue;
		/* look for particles without any flaws */
		if (p[i].flaws.nof == 0) {
			/* and remember them */
			imiss++;
            indices[cnt++] = i;
			if (imiss == 1) {
				if (!(missing = malloc(sizeof(struct Particle *)))) {
					fprintf(stderr, "Err. Cannot allocate enough mem for missing particles.\n");
					exit(1);
				} else {
					missing[0] = &p[i];
				}
			} else {
				if (!(missing = realloc(missing, sizeof(struct Particle *)*imiss))) {
					fprintf(stderr, "Err. Cannot allocate enough mem for missing particles.\n");
				} else {
					missing[imiss-1] = &p[i];
				}
			}
		}
	}
	fprintf(stderr,"imiss=%d\n",imiss);
	/* print out number of missing particles */
	if (imiss) {
		if (verbose) {
			if (imiss > 1)
				fprintf(stderr, "There are still %d particles without any flaw left.\n", imiss);
			else
				fprintf(stderr, "There is only one particle left without any flaw.\n");
		}	
	}


    /* distribute flaws to the missing particles */

    i = n_f;
    imiss_start = imiss;


    for (j = 0; j < cnt; j++) {
		activation_threshold = pow(i/(k*volume), 1./m);
        i++;
        ii = indices[j];

		if (material_type > -1) {
			if (p[ii].material_type != material_type)
				continue;
		}
		d = p[ii].flaws.nof;
		if (!(p[ii].flaws.activation_threshold = realloc(p[ii].flaws.activation_threshold, sizeof(double) * (d+1)))) {
				fprintf(stderr, "Cannot allocate enough mem for flaws.\n");
				exit(1);
		}
		p[ii].flaws.activation_threshold[d] = activation_threshold;
		p[ii].flaws.nof++;
        
    }
	free(indices);
#if 0
	/* 
	 * distribute until imiss is zero 
	 * cause each particle should have at least one flaw
	 */ 
	i = n_f;
	imiss_start = imiss;

	while (imiss) {
		/* randomly choose a particle between 0 and number */	
random2:
		random_particle_id = 0 + (int) ((1.0*number) * rand()/(RAND_MAX + 1.0));
		j = random_particle_id;
		/* check if particle has already enough flaws */
		if (p[j].flaws.nof >= maxflaws) {
			goto random2;
		}
		/* check if the particle has the wrong material_type */
		if (material_type > -1) {
			if (p[j].material_type != material_type)
				goto random2;
		}

		/* 
		 * activating threshold derived from the weibull
		 * distribution 
		 */
		activation_threshold = pow(i/(k*volume), 1./m);
		/* allocate mem for the flaw */
		d = p[j].flaws.nof;
		if (!(p[j].flaws.activation_threshold = realloc(p[j].flaws.activation_threshold, sizeof(double) * (d+1)))) {
				fprintf(stderr, "Cannot allocate enough mem for flaws.\n");
				exit(1);
		}
		p[j].flaws.activation_threshold[d] = activation_threshold;
		p[j].flaws.nof++;
		/* 
		 * check if j has been a particle without any flaw yet
		 */
		if (p[j].flaws.nof == 1) {
			/* and remove it from the missing list */
			for (d = 0; d < imiss_start; d++) {
				if (&p[j] == missing[d]) {
					missing[d] = NULL;
					imiss--;
					fprintf(stderr, "Still missing %d.\n", imiss);
				}
			}
		}
		i++;
	}
	/* free the missing list */
	for (i = 0; i < imiss_start; i++) {
		free(missing[i]);
	}
#endif // 0
	if (verbose && imiss_start) 
		fprintf(stderr, "Finally distributed %d flaws.\n", i);

	if (verbose)
		fprintf(stderr, "Mean number of flaws per particle: %le.\n", i*1.0/number);

}
