import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from google import genai
from google.genai import types


client = genai.Client(api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI")


DOCUMENT1 = """
 Operating the Climate Control System  Your Googlecar has a climate control
  system that allows you to adjust the temperature and airflow in the car.
  To operate the climate control system, use the buttons and knobs located on
  the center console.  Temperature: The temperature knob controls the
  temperature inside the car. Turn the knob clockwise to increase the
  temperature or counterclockwise to decrease the temperature.
  Airflow: The airflow knob controls the amount of airflow inside the car.
  Turn the knob clockwise to increase the airflow or counterclockwise to
  decrease the airflow. Fan speed: The fan speed knob controls the speed
  of the fan. Turn the knob clockwise to increase the fan speed or
  counterclockwise to decrease the fan speed.
  Mode: The mode button allows you to select the desired mode. The available
  modes are: Auto: The car will automatically adjust the temperature and
  airflow to maintain a comfortable level.
  Cool: The car will blow cool air into the car.
  Heat: The car will blow warm air into the car.
  Defrost: The car will blow warm air onto the windshield to defrost it.
"""

DOCUMENT2 = """
Your Googlecar has a large touchscreen display that provides access to a
  variety of features, including navigation, entertainment, and climate
  control. To use the touchscreen display, simply touch the desired icon.
  For example, you can touch the \"Navigation\" icon to get directions to
  your destination or touch the \"Music\" icon to play your favorite songs.
"""

DOCUMENT3 = """
 Shifting Gears Your Googlecar has an automatic transmission. To
  shift gears, simply move the shift lever to the desired position.
  Park: This position is used when you are parked. The wheels are locked
  and the car cannot move.
  Reverse: This position is used to back up.
  Neutral: This position is used when you are stopped at a light or in traffic.
  The car is not in gear and will not move unless you press the gas pedal.
  Drive: This position is used to drive forward.
  Low: This position is used for driving in snow or other slippery conditions.
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
