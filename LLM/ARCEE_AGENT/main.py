#!/usr/bin/env python3

# ollama server stop --system

# ollama server start

# poetry run python main.py --model <MODEL> --base_url http://127.0.0.1:11434/v1 --api_key <"KEY">

from openai import OpenAI


import argparse

import datasets

def process_dataset(
    ds: datasets.Dataset, model: str, base_url: str, api_key: str
) -> datasets.Dataset:
    """A function for processing the dataset and adding the tool calls."""

    # Initialize the OpenAI client
    client = OpenAI(base_url=base_url, api_key=api_key)

    my_answers = []

    # Call the Arcee-Agent Model you hosted to create the tool calls; you will have to call once for each row in the dataset
    for query, tools in zip(ds["query"], ds["tools"]):
        try:
            # This should work if you set up the inference server correctly
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Test for query: {query}",
                    }
                ],
                model=model,
            )
            answer=response.choices[0].message.content
            #print(f"{answer}")  
        except Exception as e:
            # Only for testing purposes, there shouldn't be any errors if you set up the inference server and called the script correctly
            print(f"Error calling the model: {e}")
            answer=f"Error for query: {query}"

        my_answers.append(answer)
    
    ds_length=len(ds)
    my_answers_length=len(my_answers)
    # Validate the length of the new column data equals to number of rows in the dataset
    if my_answers_length != ds_length:
        fill_length=ds_length-my_answers_length
        for _ in range(fill_length):
            my_answers.append("")

    # Add new column 'my_answers' with the expected tool calls to the dataset
    return ds.add_column("my_answers", my_answers)

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Generate tool calls using an LLM")
    parser.add_argument("--model", required=True, help="Name of the model to use")
    parser.add_argument(
        "--base_url",
        required=True,
        help="Base URL of the inference server, e.g. 127.0.0.1:11434/v1"
    )
    parser.add_argument(
        "--api_key", required=False, help="API key for the inference server"
        #"--api_key", required=True, help="API key for the inference server"
    )
    args = parser.parse_args()
    args
    ds = datasets.load_from_disk("./dataset/")
    assert isinstance(ds, datasets.Dataset)
    # Process the dataset and generate tool calls
    submission_ds = process_dataset(ds, args.model, args.base_url, args.api_key)
    print(submission_ds)
    # Save the resulting dataset
    submission_ds.save_to_disk("./my_dataset")

if __name__ == "__main__":
    main()
