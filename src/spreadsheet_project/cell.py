class Cell:
	def __init__(self, cell_id: str, cell_value:str = "")-> None:
		self.cell_id = cell_id
		self.cell_value = cell_value
		self.dependants = set()
		self.depended_on = set()
