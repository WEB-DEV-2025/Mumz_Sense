from agent_graph import mumz_sense_graph

# This connects to the image you just saved
input_state = {
    "input_image_path": r"D:\PROGRAMMING_WORK\Web_Developement_Folder\PERSONAL PROJECTS\Mumz Project\mumz_sense\data\test2.png" 
}

print("\n🚀 Starting Mumz-Sense Pipeline...")
result = mumz_sense_graph.invoke(input_state)

print("\n\n🏆 FINAL OUTPUT JSON:")
for rec in result.get("final_output", []):
    print(rec.model_dump_json(indent=2))