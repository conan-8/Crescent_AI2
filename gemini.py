import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from google import genai
from google.genai import types


client = genai.Client(api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI")


DOCUMENT1 = """
Atomic Structure Overview:
Atoms are composed of protons, neutrons, and electrons. A hydrogen atom has 1 proton and no neutrons, while oxygen has 8 protons and 8 neutrons.
The atomic number represents the number of protons, and the mass number is the total of protons plus neutrons.
For example:
- Carbon-12 has 6 protons and 6 neutrons (mass number = 12).
- Carbon-14 has 6 protons and 8 neutrons (mass number = 14).
Electron configuration determines chemical reactivity. Oxygen’s configuration is 1s² 2s² 2p⁴, meaning it needs 2 more electrons to complete its outer shell.
"""

DOCUMENT2 = """
Reaction Rates and Energy Changes:
The rate of a chemical reaction doubles for approximately every 10°C increase in temperature (Rule of Thumb).
For instance, if a reaction takes 60 seconds at 20°C, it would take roughly 30 seconds at 30°C.
Catalysts lower activation energy (Eₐ) without being consumed. For example, platinum catalyzes hydrogenation reactions, reducing Eₐ from 125 kJ/mol to around 60 kJ/mol.
In an exothermic reaction, energy is released to the surroundings, often shown as a negative ΔH (e.g., ΔH = -250 kJ/mol).
"""

DOCUMENT3 = """
Ideal Gas Law and Real Gases:
The ideal gas law is PV = nRT, where R = 8.314 J/(mol·K).
For 1.0 mol of gas at 298 K and 1.0 atm, the volume V ≈ 24.5 L.
Deviations occur at high pressure or low temperature. For example, at 100 atm and 250 K, real gases occupy 10–15% less volume than predicted by the ideal gas law.
According to Boyle’s Law, if the pressure on a gas doubles, its volume halves, assuming constant temperature.
"""

documents = [DOCUMENT1, DOCUMENT2, DOCUMENT3]


class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        EMBEDDING_MODEL_ID = "gemini-embedding-001"
        response = client.models.embed_content(
            model=EMBEDDING_MODEL_ID,
            contents=input,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        
        return [r.values for r in response.embeddings]


def create_chroma_db(documents, name):
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(
        name=name,
        embedding_function=GeminiEmbeddingFunction()
    )

    for i, doc in enumerate(documents):
        collection.add(documents=[doc], ids=[str(i)])
    return collection


def get_relevant_passage(query, db):
    result = db.query(query_texts=[query], n_results=1)
    return result["documents"][0][0]

def make_prompt(query, relevant_passage):
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    return f"""
You are a helpful assistant that answers questions using the reference passage below.
Keep it friendly, simple, and complete.

QUESTION: {query}
PASSAGE: {escaped}

ANSWER:
"""

def main():
    db = create_chroma_db(documents, "GoogleCarDocs")
    print("Gemini Q&A Console (type 'exit' to quit)\n")

    while True:
        query = input("Ask a question: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Cyaaaaa!")
            break

        passage = get_relevant_passage(query, db)
        prompt = make_prompt(query, passage)

        answer = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        print("\nAnswer:", answer.text.strip(), "\n")

if __name__ == "__main__":
    main()
