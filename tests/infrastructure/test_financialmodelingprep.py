import pandas as pd  

from app.infrastructure.financialmodelingprep import Financialmodelingprep

class TestFinancialmodelingprep:
  def test_findTheLowest(self):
      f = Financialmodelingprep()
    
      data = {'low':[1,2,3,1]}
      df = pd.DataFrame(data)  
    
      index = 3
      num_elements = 2
      lowest_index = f.findTheLowest(df['low'], index, num_elements)
    
      assert lowest_index == 3

      index = 2
      num_elements = 4
      lowest_index = f.findTheLowest(df['low'], index, num_elements)
    
      assert lowest_index == 1
    
def test_get_stop_loss_rows():
  f = Financialmodelingprep()
  rows = f.get_stop_loss_rows(['FB'])
  
  assert int(rows[0]["stop_loss"]) == 137