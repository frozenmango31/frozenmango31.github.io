#!/bin/bash

# A script to run rclone lsjson in parallel on multiple remotes
# and merge the results. (Simplified version without screen)

# --- Configuration ---

# List of rclone remotes to process
REMOTES=(
    dbp119: dbp121: dbp123: dbp127: dbp131: dbp134: dbp135: kdrama8: kdrama9:
    kdrama10: kdrama11: kdrama12: dbp137: kdrama13: dbp138: dbp139: dbp140:
    dbp141: ndb1: ndb2: ndb3: ndb4: ndb5: ndb6: ndb7: ndb8: ndb9: ndb10: ndb11:
    ndb12: ndb13: ndb14: ndb15: ndb16: ndb17: ndb18: ndb19: ndb20: ndb21:
    ndb22: ndb23: ndb24: ndb25: ndb26: ndb27: ndb28: ndb29: ndb30: ndb31:
    ndb32: ndb33: ndb34: ndb35: ndb36: ndb37: ndb38: ndb39: ndb40: ndb41:
    ndb42: ndb43: ndb44: ndb45: ndb46: ndb47: ndb48: ndb49: ndb50: ndb51:
    ndb52: ndb53: ndb54: xdb1: xdb2: xdb3: xdb4: xdb5: xdb6: xdb7: xdb8:
    xdb9: xdb10: xdb11: xdb11b: xdb12: xdb13: xdb14: xdb15: xdb16: xdb17:
    xdb18: xdb19: xdb20: xdb21: xdb22: xdb23: xdb24: xdb25: xdb26: xdb27:
)

# Directory to store the individual JSON files
OUTPUT_DIR="json_outputs"
# Final merged JSON file
MERGED_FILE="all_files.json"

# --- Script Logic ---

# 1. Create the output directory
mkdir -p "$OUTPUT_DIR"
echo "✅ Created output directory: $OUTPUT_DIR"

# 2. Start all rclone processes in the background
echo "🚀 Starting rclone lsjson for ${#REMOTES[@]} remotes in parallel..."
for remote in "${REMOTES[@]}"; do
    # Sanitize remote name for the filename (removes ':')
    clean_name="${remote//:/}"
    output_file="${OUTPUT_DIR}/${clean_name}.json"

    echo "   -> Starting process for $remote"
    
    # Run the command in a subshell and send it to the background with '&'
    (
      rclone lsjson -R \
        --filter "+ asiandrama/**" \
        --filter "+ kdrama/**" \
        --filter "+ misc/**" \
        --filter "+ movies/**" \
        --filter "+ tvs/**" \
        --filter "- **" \
        "$remote" > "$output_file"
    ) &
done

# 3. Wait for all background jobs to complete
echo -e "\n⏳ Waiting for all rclone jobs to finish. This can take a very long time..."
wait
echo -e "\n🎉 All rclone jobs have finished."

# 4. Merge the JSON files
echo "🔄 Merging all JSON files into '$MERGED_FILE'..."
if [ -z "$(ls -A ${OUTPUT_DIR}/*.json 2>/dev/null)" ]; then
    echo "❌ Error: No JSON files were generated in the '${OUTPUT_DIR}' directory. The final file cannot be created."
    exit 1
fi

# 'jq -s add' slurps all input files into an array and then adds (concatenates) them.
jq -s 'add' "${OUTPUT_DIR}"/*.json > "$MERGED_FILE"

if [ $? -eq 0 ]; then
    file_count=$(ls -1q "${OUTPUT_DIR}"/*.json | wc -l)
    echo "✅ Success! Merged $file_count JSON files."
    echo "Final output is in '$MERGED_FILE'."
else
    echo "❌ Error: Failed to merge JSON files. Please check for errors in the '$OUTPUT_DIR' directory."
    exit 1
fi

echo "Script complete."