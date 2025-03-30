
import sys
import os
import pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apps.langchain_bot.phases.context.vectors_store_sentence_transformer import DocumentRetriever
#from apps.langchain_bot.dependencies import document_retriever
import unittest

class TestContext(unittest.TestCase):
    
    def setUp(self):
        self.document_retriever = DocumentRetriever()
    def test_context_accuracy(self):
        # Example question
        question = "How many institutions are there in Boston city?" #try different questions, for loop
        # Expected context
        expected_context = """1. Table: ic2022campuses\n   Column Name: ['unitid', 'campusid', 'pcinstnm', 'pcaddr', 'pccity', 'pcstabbr', 'pczip', 'pcfips', 'pcobereg', 'pcchfnm', 'pcchftitle', 'pcgentele', 'pcein', 'pcueis', 'pcopeid', 'pcopeflag', 'oldunitid', 'pcwebaddr', 'pcadminurl', 'pcfaidurl', 'pcapplurl', 'pcnpricurl', 'pcveturl', 'pcathurl', 'pcdisaurl', 'pcsector', 'pciclevel', 'pccontrol', 'pchloffer', 'pcugoffer', 'pcgroffer', 'pchdegofr1', 'pcdeggrant', 'pchbcu', 'pctribal', 'pclocale', 'pcopenpubl', 'pcact', 'pccyactive', 'pcpostsec', 'pcpseflag', 'pcpset4flg', 'pccbsa', 'pccbsatype', 'pccsa', 'pccountycd', 'pccountynm', 'pccngdstcd', 'pclongitud', 'pclatitude', 'pclevel1', 'pclevel1a', 'pclevel1b', 'pclevel2', 'pclevel3', 'pclevel4', 'pclevel5', 'pclevel6', 'pclevel7', 'pclevel8', 'pclevel17', 'pclevel18', 'pclevel19', 'pcft_ftug', 'pcalloncam', 'pcapplfeeu', 'pcroom', 'pcchg1at0', 'pcchg1af0', 'pcchg1ay0', 'pcchg1at1', 'pcchg1af1', 'pcchg1ay1', 'pcchg1at2', 'pcchg1af2', 'pcchg1ay2', 'pcchg1at3', 'pcchg1af3', 'pcchg1ay3', 'pcchg1tgtd', 'pcchg1fgtd', 'pcchg2at0', 'pcchg2af0', 'pcchg2ay0', 'pcchg2at1', 'pcchg2af1', 'pcchg2ay1', 'pcchg2at2', 'pcchg2af2', 'pcchg2ay2', 'pcchg2at3', 'pcchg2af3', 'pcchg2ay3', 'pcchg2tgtd', 'pcchg2fgtd', 'pcchg3at0', 'pcchg3af0', 'pcchg3ay0', 'pcchg3at1', 'pcchg3af1', 'pcchg3ay1', 'pcchg3at2', 'pcchg3af2', 'pcchg3ay2', 'pcchg3at3', 'pcchg3af3', 'pcchg3ay3', 'pcchg3tgtd', 'pcchg3fgtd', 'pcchg4ay0', 'pcchg4ay1', 'pcchg4ay2', 'pcchg4ay3', 'pcchg5ay0', 'pcchg5ay1', 'pcchg5ay2', 'pcchg5ay3', 'pcchg6ay0', 'pcchg6ay1', 'pcchg6ay2', 'pcchg6ay3', 'pcchg7ay0', 'pcchg7ay1', 'pcchg7ay2', 'pcchg7ay3', 'pcchg8ay0', 'pcchg8ay1', 'pcchg8ay2', 'pcchg8ay3', 'pcchg9ay0', 'pcchg9ay1', 'pcchg9ay2', 'pcchg9ay3', 'pccipcode1', 'pcciplgth1', 'pcprgmsr1', 'pcmthcmp1', 'pcwkcmp1', 'pclnayhr1', 'pclnaywk1', 'pcchg1py0', 'pcchg1py1', 'pcchg1py2', 'pcchg1py3', 'pcchg4py0', 'pcchg4py1', 'pcchg4py2', 'pcchg4py3', 'pcchg5py0', 'pcchg5py1', 'pcchg5py2', 'pcchg5py3', 'pcchg6py0', 'pcchg6py1', 'pcchg6py2', 'pcchg6py3', 'pcchg7py0', 'pcchg7py1', 'pcchg7py2', 'pcchg7py3', 'pcchg8py0', 'pcchg8py1', 'pcchg8py2', 'pcchg8py3', 'pcchg9py0', 'pcchg9py1', 'pcchg9py2', 'pcchg9py3']
        """
        #
        #expected context="""
        #Columns: ['Table_description', 'Coloum description']
        #"""
        self.document_retriever.table_formatter.docs2str=lambda x: x  #mocking
    
        # Retrieve the context for the top-k documents
        context_k1 = self.document_retriever.find_top_k_similar(question, k=1)
        pprint.pprint(context_k1)
        self.assertIsInstance(context_k1, str) 
        
        

        # Normalize text for comparison
        expected_clean = expected_context.strip().lower()
        retrieved_clean = context_k1.strip().lower()


 
 # Debugging: Print expected and retrieved context
        #print("Expected clean:\n", expected_clean)
        #print("Retrieved clean:\n",retrieved_clean )
        
        # # Check if the expected context is a part of the retrieved context
        self.assertTrue(expected_clean in retrieved_clean,
                      f"Expected context not found in retrieved context:\nExpected: {expected_context}\nRetrieved: {context_k1}")
        
        
       # self.assertTrue(expected_context.strip() in context_k1.strip(), 
                        #f"Expected context not found in retrieved context: {context_k1}")
        
       
if __name__ == "__main__":
   unittest.main()
  