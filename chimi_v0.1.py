import json
from difflib import get_close_matches

# load the JSON file or create a default one if it doesn't exist
def load_knowledge_base(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()
            if not content:
                raise ValueError("File is empty")
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        # Start fresh if file is missing, broken, or empty
        print("Chimi: Creating new knowledge base...")
        base = {"questions": []}
        save_knowledge_base(file_path, base)
        return base


# save the knowledge base back to the file
def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


# find the best matching question from memory
def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None
33
# get the saved answer for a matched question
def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]

def edit_answer(question: str, new_answer: str, knowledge_base: dict) -> bool:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            q["answer"] = new_answer
            return True
    return False

def forget_question(question: str, knowledge_base: dict) -> bool:
    for i, q in enumerate(knowledge_base["questions"]):
        if q["question"] == question:
            del knowledge_base["questions"][i]
            return True
    return False


# main chatbot loop
def chimi():
    knowledge_base = load_knowledge_base('knowledge_base.json')

    print("Chimi: Hi, I'm Chimi! Ask me anything or teach me something new.")
    print("Type 'quit' to exit.")
    print("Type 'edit [question]' to change an answer or 'forget [question]' to delete one.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'quit':
            print("Chimi: Goodbye!")
            break

        if user_input.lower().startswith("edit "):
            target_question = user_input[5:].strip()
            match = find_best_match(target_question, [q["question"] for q in knowledge_base["questions"]])
            if match:
                print(f"Chimi: Found '{match}'. What's the new answer?")
                new_answer = input("You: ").strip()
                if edit_answer(match, new_answer, knowledge_base):
                    save_knowledge_base('knowledge_base.json', knowledge_base)
                    print("Chimi: Got it! I updated the answer.")
            else:
                print("Chimi: I couldn't find a question like that.")

        elif user_input.lower().startswith("forget "):
            target_question = user_input[7:].strip()
            match = find_best_match(target_question, [q["question"] for q in knowledge_base["questions"]])
            if match:
                confirm = input(f"Chimi: Are you sure you want me to forget '{match}'? (yes/no): ").strip().lower()
                if confirm == "yes":
                    if forget_question(match, knowledge_base):
                        save_knowledge_base('knowledge_base.json', knowledge_base)
                        print("Chimi: It's forgotten.")
                    else:
                        print("Chimi: I couldn't forget that.")
                else:
                    print("Chimi: Okay, I won't forget it.")
            else:
                print("Chimi: I couldn't find a question like that.")

        all_questions = [q["question"] for q in knowledge_base["questions"]]

        if user_input in all_questions:
            best_match = user_input
        else:
            best_match = find_best_match(user_input, all_questions)


        if best_match:
            answer = get_answer_for_question(best_match, knowledge_base)
            print(f"Chimi: {answer}")
        else:
            print("Chimi: I don't know the answer. Can you teach me?")
            new_answer = input("Type the answer or 'skip' to skip: ").strip()

            if new_answer.lower() != 'skip':
                knowledge_base["questions"].append({
                    "question": user_input,
                    "answer": new_answer
                })
                save_knowledge_base('knowledge_base.json', knowledge_base)
                print("Chimi: Thank you! I learned something new!")

if __name__ == '__main__':
    chimi()
