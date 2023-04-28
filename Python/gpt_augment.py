import openai
import tiktoken
import time
import sys

labels = open((sys.argv[1] if len(sys.argv) > 1 else "../data/rip_data/character_desc.txt"), "r").read().split('\n')

openai.api_key=open('../data/gpt3_api_key.txt', "r").read().strip()       # enter open ai API key here :)

# prompt = """I am going to provide you with a list of strings that have labels. 
#             These labels describe images of emojis. Your task is to take each string in the list provided, 
#             and return me a new list of the same size with alternate labels. 
#             These alternate labels should describe the same image as the original label, 
#             but use different words or synonyms when appropriate. 
#             For example, alternate labels for "angry face" could be "mad face", "face that is angry", or "scowling face"."""

prompt = """
        I am going to provide you with a list of strings that have labels.
        They are describing a video game character's appearance.  
        For each label, can you give me 5 different ways to say these same descriptions in a similar format as the way it was given to you but with different words or synonyms?
        For example, alternate labels for a "a man with a red shirt" could be "a man wearin a shirt that is red", "a male human donning a scarlet shirt", or "a male-presenting person sporting a crimson top".
        """

messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt + " Write your output in the form of a list with each group of labels separated by an '&' character. ONLY OUTPUT THE LIST. Here is the list of labels:"}
         ]
            

# Get prompt length
def num_tokens_from_messages(messages):
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

# pretty fucking slow but gets the job done to always segment as necessary
def segment_arr(labels, threshold):
    encoding = tiktoken.get_encoding("cl100k_base")

    arr = []
    total = []

    for i, label in enumerate(labels):
        arr.append(label)
        if len(encoding.encode(f"{arr}")) > threshold:
            hold = arr.pop()
            if (size := len(encoding.encode(f"{[hold]}"))) > threshold:
                raise Exception(f"Element at position *{i}*, *'{[hold]}'* is too big: *{size} tokens* for this threshold: *{threshold} tokens*")
            total.append(arr)
            arr = [hold] 
    total.append(arr)
    return total

def get_new_embeds(arr):

	start = time.time()
	size = num_tokens_from_messages(messages)
	labels = segment_arr(arr, 2000 - size)
	print(f"split time = {time.time() - start}")
	res, ans_arr = [], []

	for i, label in enumerate(labels):
		print(f"Loop {i} running through array of size {len(label)}")

		result = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=[
			{"role": "system", "content": "You are a helpful assistant."},
			{"role": "user", "content": prompt + " Write your output in the form of a list with each group of labels separated by an '&' character. ONLY OUTPUT THE LIST. Here is the list of labels:" + f"{label}"},
			]
		)

		answer = result.choices[0]['message']['content']
		ans_arr.append(answer)
		res += eval(answer[answer.find("["):answer.find(']')+1])

	return res, ans_arr

result, ans_arr = get_new_embeds(labels)
with open("output_arr_format.txt", "w") as f:
	f.write(f"{result}")
with open("output.txt", "w") as f:
	for line in result:
		f.write(line + "\n")
with open("answers.txt", "w") as f:
	for a in ans_arr:
		f.write(a + "\n")
