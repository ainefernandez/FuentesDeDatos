import os
import re
import gzip
import magic
import numpy as np
import pandas as pd
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from scipy import spatial

class WordRelate:
    """
    This class implements all the necessary functionality
    to perform similarity analysis between words using distributed representations.
    """

    def __init__(self, home_dir='C:\\Users\\santi\\Desktop\\Semestre6\\GitHubFD\\FuentesDeDatos\\projects\\project_2'):
        self.home_dir = home_dir
        self.data_path = os.path.join(self.home_dir, 'data', 'text_comp', 'texts')
        self.fig_path = os.path.join(self.home_dir, 'figs')
        # -----------------------------------
        # We'll store all our results at a collection based level i.e.
        # we are going to access every structure within the class
        # using the collection id as keys.
        # TODO
        # Initialize the values (empty dics) for
        # - voc
        # - ivoc
        # - collections
        # - vrm
        # - reduced_vrm
        # (5 points)
        # -----------------------------------
        # Your code goes here (~ 1 - 5 lines)
        self.voc = {}
        self.ivoc = {}
        self.collections = {}
        self.vrm = {}
        self.reduced_vrm = {}
        
        print(f"Files found in storage: \n {os.listdir(self.data_path)}")


    def proc_line(self, line):
        '''
        This function parses each input line:
        - sets every word into lowercase
        - remove non words (except single white space)
        - remove empty lines
        - returns a list of words.
        :param line: the line to process
        :return: processed line
        '''
        # -----------------------------------
        # TODO
        # complete the parsers, currently, each word
        # line is outputed as it is.
        # (10 points)
        # -----------------------------------
        parsed_lines = [re.search(r'([a-zA-z]+)', x.lower()).group(0) for x in line.split()]
        # Your code goes here (~ 1 line)
        return parsed_lines


    def get_voc(self, collection_id, sw, top_freq_words=2000):
        '''
        Get a series with the most common words in the collection.
        :param collection_id: the id of the collection to process
        :param sw: list of stop words
        :param freq_words: maximum number of words to include in output
        :return:
            - self.voc: a series containing the vocabulary: {word: index},
            - self.ivoc: a series containgin the vocabulary: {index: word} (this will be handy for word retrieval)
        '''
        # -----------------------------------
        # TODO
        # Parse the texts in the collection and
        # build a series with the top_freq_words.
        # Sort the index of voc based on the words.
        # Sort the index of ivoc based on the numerical value.
        # (10 points)
        # -----------------------------------
        #ESTO ESTÁ HECHO SOBRE UNA SOLA COLECCION POR COLLECTION ID
        palabras = []
        for text in self.collections[collection_id]:
            palabras = palabras + [t for t in text if t not in sw]
        
        ##Este cacho (las siguientes 4 instrucciones) es sacado de su versión
        palabrasCount = pd.Series(palabras).value_counts()
        palabras = palabrasCount[0:top_freq_words]

                
        # # # Make order monotonic to improve performance.
        self.voc[collection_id] = pd.Series(range(len(palabras)), index=palabras.index).sort_index()

        #Get inverse index for word vocs
        self.ivoc[collection_id] = pd.Series(self.voc[collection_id].index,
                                             index=self.voc[collection_id].values).sort_index()
        ##Aquí termina lo sacado de su versión

        # # Get inverse index for word vocs
        print(f'Monotonic index:{self.voc[collection_id].index.is_monotonic}')        
        return list(self.ivoc[collection_id].index)


    def dist_rep(self, collection_id, ws=4):
        '''
        In this function we get the distributed representation of words based on
        cooccurrence along windows of size ws. This is the most
        challenging question in the project.
        Check https://aclanthology.org/W14-1503.pdf for best practices on this methodology.
        :param collection_id:
        :param ws: size of the context window
        :return:
         - self.vrm: a vectorized representation of the words
        '''
        voc_size = len(self.voc[collection_id])
        self.vrm[collection_id] = np.zeros((voc_size, voc_size))
        for text in self.collections[collection_id]:
            texto = [w for w in text if w in self.voc[collection_id]]
            
            # -----------------------------------
            # TODO
            # For each word in text, build a window
            # of size 2*ws. Containing the vocabulary indexes of ws words prior to the word
            # of interest and ws words after. For example
            # test = [START this is very a simple example]
            # w = this
            # the output window should contain the indexes of the words
            # START, is, very, a, simple.
            # Be sure to structure your output as follows:
            # (iw_c, (iw_in1, iw_in2, ..., iw_inN), (cw_in1, cw_in2, ..., cw_inN))
            # where
            # - iw_c: is the voc index of the central word of the window
            # - iw_ini: is the voc index of the i'th word in the window
            # - cw_ini: is the number of times w_ini appears in the window
            # (35 points)
            # Compare your results with the precomputed matrizes at:
            # ./home_dir/data/tests
            # np.array_equal
            # -----------------------------------
            
            # Your code goes here ( 1 ~ 10 lines)
            #Build the Window

            indexes = []
            for i,w in enumerate(texto):
                if ws*2 > len(texto):
                    window = [j for j in range(0,len(texto)) if j!=i]
                    words = [texto[p] for p in window]
                else:
                    if i<=ws:
                        window = [j for j in range(0,ws+i+1) if j!=i]
                        words = [texto[p] for p in window]
                    else:
                        if i+ws > len(texto):
                            window = [j for j in range(i-ws,len(texto)) if j!=i]
                            words = [texto[p] for p in window]
                        else:
                            window = [j for j in range(i-ws,min((ws+i+1),len(texto))) if j!=i]
                            words = [texto[p] for p in window]    
        
                index = self.voc[collection_id][w]
                
                index1 = []
                index2 = []
                    
                for v in window:
                    index1.append(self.voc[collection_id][texto[v]])
                    index2.append(words.count(texto[v]))
                indexes.append((index,(index1,index2)))
            
            for word,(related,values) in indexes:
                print(word)
                # -----------------------------------
                # TODO
                # Update the count values in self.vrm.
                # (10 points)
                # -----------------------------------
                
                #Esta línea la puse como usted aunque creo que ya funcionaba la que yo tenía
                self.vrm[collection_id][word,related] = self.vrm[collection_id][word,related] + values

        return self.vrm[collection_id]

    def ppmi_reweight(self, collection_id):
        '''
        In this section we apply ppmi transformation to vrm
        '''
        # -----------------------------------
        # TODO
        # Compute the matrix of expected counts to
        # update vrm.
        # expected_i_j = (row_sum_i*col_sum_j)/tot_sum
        # (15 points)
        # -----------------------------------

        # Your code goes here (~ 1 - 4 lines)
        expected = np.zeros((len(self.vrm[collection_id]),len(self.vrm[collection_id])))
        for i in range(len(self.vrm[collection_id])):
            for j in range(len(self.vrm[collection_id][0])):
                expected[i][j] = ((self.vrm[collection_id].sum(axis=1))[i]*(self.vrm[collection_id].sum(axis=0)))[j]/(self.vrm[collection_id].sum())
        
        with np.errstate(divide='ignore'):
            log_vals = np.log(self.vrm[collection_id]/expected)
        self.vrm[collection_id] = np.maximum(log_vals, 0)
    
    def dim_redux(self, collection_id, dim_reducer='pca'):
        '''
        Apply dimensionality reduction
        :return:
        '''
        if dim_reducer == 'tsne':
            self.reduced_vrm[collection_id] = TSNE(n_components=2,
                                                   init='random').fit_transform(self.vrm[collection_id])
        if dim_reducer == 'pca':
            self.reduced_vrm[collection_id] = PCA(n_components=2).fit_transform(self.vrm[collection_id])

    def plot_reps(self):
        '''
        Plots the reduced representations computed for each collection
        :return:
        '''

        if not os.path.isdir(self.fig_path):
            print('Making figure directory')
            os.mkdir(self.fig_path)

        for i, collection in enumerate(self.collections.keys()):
            fig, ax = plt.subplots(figsize=(12, 10))
            x = self.reduced_vrm[collection][:, 0]
            y = self.reduced_vrm[collection][:, 1]
            ax.scatter(x, y)
            for i, txt in enumerate(self.ivoc[collection]):
                ax.annotate(txt, (x[i], y[i]))
            print(f'saving figure {collection}')
            fig.savefig(os.path.join(self.fig_path, f'{collection}.png'))


    def make_bulk_collections(self):
        '''
        Unifies all collections in one single collection with key 'BULK'
        :return:
        '''
        bulk = []
        for i, collection in enumerate(self.collections.keys()):
                bulk += self.collections[collection]
        self.collections['BULK'] = bulk


    def get_word_relatedness(self, collection):
        '''
        :param word_relate_path:
        :return:
        '''
        word_relate_path = os.path.join(self.home_dir, 'data','relatedness', 'wr.csv')
        wr = pd.read_csv(word_relate_path)
        for index, row in wr.iterrows():
            w1 = row.word1
            w2 = row.word2
            s  = row.score
            # Check if words are in voc
            annotated_sim = []
            predicted_sim = []
            print(w1)
            print(w2)
            if (w1 in self.voc[collection]) and (w2 in self.voc[collection]):
                annotated_sim.append(s)
                similarity = spatial.distance.cosine(wc.vrm[collection][wc.voc[collection][w2]],
                                                     wc.vrm[collection][wc.voc[collection][w1]])
                predicted_sim.append(similarity)
        correlation = np.corrcoef(np.array(annotated_sim), np.array(predicted_sim))[0, 1]
        print(f'Found {len(predicted_sim)} words to relate in voc. Pearson Correlation: {correlation}')
        return correlation

    def read_collection(self, collection_id):
        print(self.data_path)
        print(type(self.data_path))
        print(collection_id)
        collection_path = os.path.join(self.data_path, collection_id)
        # Read each file in collection
        texts = []
        for file in os.listdir(collection_path):
            file_path = os.path.join(collection_path, file, 'main_text.txt')
            # Take care of gzipped files
            if re.match(r'^gzip', magic.from_file(file_path)):
                with gzip.open(file_path, 'rb') as f:
                    lines = f.read()
            else:
                with open(file_path, encoding="utf-8") as f:
                    # Read lines and process them. (notice we are removing empty lines)
                    lines = f.readlines()
        # -----------------------------------
        # TODO
        # - Call proc line on each line of input
        # - Make sure to add 'START' and 'END' tokens to the start and end of each sentence.
        # - Preserve only non empty lines.
        # (15 points)
        # -----------------------------------
        
        #Your code goes here (~ 1 - 3 lines)
        for l in lines:
             r = ['START']
             r = r + self.proc_line(l)
             r = r + ['END']
             texts.append(r)
        # Add texts to the collections.
        self.collections[collection_id] = texts


if __name__ == '__main__':
    # Check available collections
    collections = os.listdir(os.path.join('C:\\Users\\santi\\Desktop\\Semestre6\\GitHubFD\\FuentesDeDatos\\projects\\project_2','data', 'text_comp', 'texts'))
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument('--collection',
                        choices=collections)
        
    args = parser.parse_args()
    # Read stopwords
    with open('C:\\Users\\santi\\Desktop\\Semestre6\\GitHubFD\\FuentesDeDatos\\projects\\project_2\\data\\stop_words\\stopwords.txt') as f:
        stopwords = f.read().split('\n')
    # Instantiate WordRelate object
    wc = WordRelate()
    # Read collection argument 
    collection = args.collection

    # -----------------------------------
    # TODO
    # -----------------------------------
    # 1.- read collection 00
    # 2.- get vocabularies
    # 3.- generate distributed representations
    # 4.- apply ppmi
    # 5.- apply dimensionality reduction
    # 6.- Plot results
    # To test your execution run:
    # ./wordrelatedness --collection '[collection_id]'
    # Your final output should produce two plots
    # such as the one displayed in:
    # ./home_dir/figs/.
    # -----------------------------------
    collection = 'proj_eval'
    # Your code goes here (~ 7 lines)
    wc.read_collection(collection)
    palabras = wc.get_voc(collection, stopwords)
    x = wc.dist_rep(collection,4)
    x = pd.DataFrame(x.T,index=palabras,columns=palabras)
    wc.dim_redux(collection)
    wc.ppmi_reweight(collection)
    wc.plot_reps()
