import os, csv
from biorun import utils, const
from biorun.libs import placlib as plac

try:
    from goatools.cli.find_enrichment import GoeaCliFnc
    from goatools.cli.gosubdag_plot import PlotCli
    from goatools.obo_parser import GODag
    from goatools.godag.consts import RELATIONSHIP_SET
    from goatools.multiple_testing import Methods
    from goatools.pvalcalc import FisherFactory
    from goatools.cli.find_enrichment import GoeaCliArgs
    from goatools.anno.factory import get_anno_desc
    from goatools.anno.idtogos_reader import AnnoReaderBase, IdToGosReader, InitAssc

except ImportError as exc:
    utils.error("Goa tools needs to be installed to use this library.")

logger = utils.logger

ASSOC_DIR = os.path.join(utils.DATADIR, 'association')

join = os.path.join

# Data directory with existing obo file.
GO_FILE = "go.obo"

GO_FILE = join(utils.DATADIR, GO_FILE)

os.makedirs(ASSOC_DIR, exist_ok=True)


class Bunch(object):

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


class BioAssc(InitAssc):
    ASSC = {}

    def __init__(self, assc, godag, namespaces, fin_anno=None):
        BioAssc.ASSC = assc

        super(BioAssc, self).__init__(fin_anno, godag, namespaces)

    @staticmethod
    def _init_id2gos(assoc_fn):
        return BioAssc.ASSC


class BioReader(IdToGosReader):

    def __init__(self, assc, filename=None, **kws):
        self.assc = assc
        super(BioReader, self).__init__(filename=filename, **kws)

    def _init_associations(self, filename, **kws):
        ini = BioAssc(godag=kws['godag'], namespaces=kws['namespaces'], assc=self.assc)
        self.id2gos = ini.id2gos
        return ini.nts


class BioCliFun(GoeaCliFnc):
    """
    Wrapper to initialize population, study and association as Python objects
    instead of files.
    """

    def __init__(self, args, study, pop, assc):
        self.study = study
        self.population = pop
        self.assc = assc
        super(BioCliFun, self).__init__(args=args)

    def _get_objanno(self, assoc_fn):
        """
        Get an annotation object
        """
        anno_type = "id2gos"
        # # Default annotation file format is id2gos
        # if anno_type is None:
        #     anno_type = 'id2gos'
        # kws: namespaces taxid godag
        kws = self._get_kws_objanno(anno_type)

        return self.__annon(anno_type, **kws)

    def __annon(self, anno_type, **kws):
        """Read annotations in GAF, GPAD, Entrez gene2go, or text format."""
        # kws get_objanno: taxids hdr_only prt allow_missing_symbol
        # anno_type = get_anno_desc(fin_anno, anno_type)

        if anno_type == 'id2gos':
            kws_id2go = {k: kws[k] for k in BioReader.exp_kws.intersection(kws.keys())}

            return BioReader(assc=self.assc, **kws_id2go)

        raise RuntimeError('UNEXPECTED ANNOTATION FILE FORMAT')

    def rd_files(self, study_fn, pop_fn):
        """
        Set the study and population objects
        """

        print("Study: {0} vs. Population {1}\n".format(len(self.study), len(self.population)))
        return self.study, self.population


def get_study(association, size=5):
    """
    Return most annotated genes from association dict
    """
    most_annotated = sorted(association.keys(), key=lambda i: len(association[i]), reverse=True)
    study = most_annotated[:size]
    study = frozenset(study)
    print(f"*** Using the {size} most annotated genes as study: {','.join(study)} ")
    return study


def parse_data(fname, study_size=10):
    """
    Take a .gaf file and return an association dictionary and population dict.
    """

    if not os.path.isfile(fname):
        utils.error("Association file needs to be downloaded first.")

    # Read the population from file
    association = {}
    population = set()

    stream = utils.gz_read(fname, 'r')
    print(f"*** parsing {fname}")
    # Get the gene from each row
    for line in stream:
        line = line.decode()
        if line.startswith('!'):
            continue
        gene = line.split('\t')[2]
        goterm = line.split('\t')[4]

        association.setdefault(gene, set()).update([goterm])
        population.update([gene])

    return population, association


def get_fname(name):
    url = const.ASSOCIATION_MAP.get(name)

    # Download association to file.

    fname = os.path.basename(url)

    dest = os.path.join(ASSOC_DIR, fname)
    return dest


def download_gaf(name):
    """
    Download gaf file
    """
    dest = get_fname(name)
    url = const.ASSOCIATION_MAP.get(name)

    utils.download(url=url, dest_name=dest)

    return


def download_terms():
    """
    Download go terms
    """

    if os.path.exists(GO_FILE):
        print(f"*** File already found at {GO_FILE}")

    return


def preform_enrichment(args, pop, assc, study):
    # Put the kwargs in a namespace for goatools

    # Get data from databse or saved file

    obj = BioCliFun(args=args, pop=pop, assc=assc, study=study)

    # Reduce results to significant results (pval<value)
    results_specified = obj.get_results()

    # Print results in a flat list
    obj.prt_results(results_specified)

    # Plot the

    return


def plot_enrichment(kwargs):
    kws_plt = dict(obo=GO_FILE, )
    godag_optional_attrs = PlotCli._get_optional_attrs(kwargs)

    godag = GODag(GO_FILE, godag_optional_attrs)

    PlotCli().plot(godag=godag, kws_plt=kws_plt)

    return


@plac.pos('study', "Gene names in a study")
@plac.pos('name', "Association to map gene name to a GO category, also used to build the population.",
          choices=const.ASSOCIATION_MAP.keys())
@plac.flg('download', "download gaf file")
@plac.flg('build', "Build database from available GAF files")
@plac.flg('enrich', "Find GO enrichment of genes under study", abbrev='x')
@plac.flg('prtstd',
          help=('Print GO terms only if they are associated with study genes. '
                'This is useful if printng all GO results '
                'regardless of their significance (--pval=1.0). '), abbrev="S")
@plac.flg('indent', help="indent GO terms", abbrev='I')
@plac.flg('noprop', help="Do not propagate counts to parent terms", abbrev='N')
# # no -r:   args.relationship == False
# # -r seen: args.relationship == True
@plac.flg('relationship', help="Propagate counts up all relationships and plot all terms", abbrev="E")
@plac.flg('compare',
          help="the population file as a comparison group. if this "
               "flag is specified, the population is used as the study "
               "plus the `population/comparison`")
@plac.opt('inc', help="Include specified evidence codes and groups separated by commas", abbrev='C')
@plac.opt('exc', help="Exclude specified evidence codes and groups separated by commas")
@plac.opt('taxid', "When using NCBI's gene2go annotation file, specify desired taxid")
@plac.opt('alpha', type=float, help='Test-wise alpha for multiple testing', abbrev='A')
@plac.opt('pval', type=float, help="""Only print results with uncorrected p-value < PVAL.
                                        Print all results, significant and otherwise, by setting --pval=1.0""")
@plac.opt('field', type=str, help='Only print results when PVAL_FIELD < PVAL.')
@plac.opt('outfile', type=str, help='Write enrichment results into xlsx or tsv file')
@plac.opt('ns', type=str,
          help='Limit GOEA to specified branch categories. '
               'BP=Biological Process; '
               'MF=Molecular Function; '
               'CC=Cellular Component')
@plac.opt('id2sym', type=str, help='ASCII file containing one geneid and its symbol per line')
@plac.opt('sections', type=str,
          help=('Use sections file for printing grouped GOEA results. '
                'Example SECTIONS values:\n'
                'goatools.test_data.sections.gjoneska_pfenning \n'
                'goatools/test_data/sections/gjoneska_pfenning.py \n'
                'data/gjoneska_pfenning/sections_in.txt\n'))
@plac.opt('detail', type=str,
          help=('Write enrichment results into a text file \n'
                'containing the following information: \n'
                '1) GOEA GO terms, grouped into sections \n\n'
                '2) List of genes and ASCII art showing section membership \n'
                '3) Detailed list of each gene and GO terms w/their P-values \n'),
          abbrev='D')
@plac.opt('ratio', type=float,
          help="only show values where the difference between study "
               "and population ratios is greater than this. useful for "
               "excluding GO categories with small differences, but "
               "containing large numbers of genes. should be a value "
               "between 1 and 2. ")
@plac.opt('relationships', abbrev='R',
          help=('Propagate counts up user-specified relationships ( comma separated ), which include: '
                '{RELS}').format(RELS=' '.join(RELATIONSHIP_SET)))
@plac.opt('method', type=str, help=Methods().getmsg_valid_methods())
@plac.opt('pvalcalc', type=str, help=str(FisherFactory()), abbrev='P')
@plac.opt('min_overlap', type=float,
          help="Check that a minimum amount of study genes are in the population",
          abbrev='M')
@plac.opt('goslim', type=str, help="The GO slim file is used when grouping GO terms.")
def run(name='human', taxid=9606, download=False,
        alpha=0.05, pval=.05, field='p_uncorrected', outfile='result.tsv',
        ns='BP,MF,CC', id2sym=None, detail='', sections=None,
        compare=False, ratio=None, prtstd=False, indent=False,
        noprop=False, relationship=False, relationships='',
        enrich=False, method="bonferroni,sidak,holm,fdr_bh", pvalcalc="fisher",
        min_overlap=0.7, goslim='goslim_generic.obo', inc='', exc='',
        *study):
    # Construct arguments to pass down to GO.
    go_params = dict(alpha=alpha, pval=pval, pval_field=field, outfile=outfile,
                     ns=ns, id2sym=id2sym, outfile_detail=detail,
                     sections=sections, compare=compare, ratio=ratio, taxid=taxid,
                     prt_study_gos_only=prtstd, indent=indent, filenames=[None, None, None],
                     obo=GO_FILE, no_propagate_counts=noprop, relationship=relationship,
                     relationships=relationships, method=method, pvalcalc=pvalcalc,
                     min_overlap=min_overlap, goslim=goslim, ev_inc=inc, ev_exc=exc)

    go_args = Bunch(**go_params)

    if download:
        download_gaf(name=name)
        return

    # Get the GAF file name
    fname = get_fname(name)

    # Parse the association, population, and default study
    population, association = parse_data(fname=fname)

    # Get the 5 most annotated genes when no study is given

    study = frozenset(study) or get_study(association=association)

    preform_enrichment(args=go_args, pop=population, assc=association, study=study)
    return
