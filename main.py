from core.build_graph import build_graph
import json


def main():

    app = build_graph()
    person_name = "areeb"
    
    # Initial state
    initial_state = {
        "raw_resume_text": None,
        "resume_path": f"storage/resumes/{person_name}.pdf",
        "candidate_profile": None
    }
    
    # Run the workflow
    result_state = app.invoke(initial_state)

    # get the result
    result = result_state["candidate_profile"].model_dump()

    # print(result)
    print("\n\nresult_state: \n\n", result_state)

    # save the result to a file
    with open(f"storage/results/{person_name}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    main()
    print("\n\nDone")
