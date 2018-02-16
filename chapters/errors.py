class TestCode():

	def __init__(self, ch_num, req_num, description = ""):

		self.ch = ch_num
		self.req = req_num
		self.description = description

	def __str__(self):

		message = "chapter " + str(self.ch) + ", requirement " + str(self.req)
		if self.description:
			message +="\n\t" + self.description

		return message

	def __repr__(self):
		return self.__str__()


class TestError(Exception):

	def __init__(self, testCodeList):

		super(TestError, self).__init__()

		self.testCodeList = testCodeList

	def __str__(self):

		message = "\n"

		for testCode in self.testCodeList:
			message += "Failed Test: " + testCode.__str__() + "\n"

		return message

	def __repr__(self):
		return self.__str__()

def main():

	raise TestError([TestCode(1,1,"testing123"), TestCode(1,2)])


if __name__ == "__main__":
	main()