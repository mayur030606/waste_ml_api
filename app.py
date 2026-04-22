@app.route('/compare-images', methods=['POST'])
def compare():
    before_path = f"before_{uuid.uuid4().hex}.jpg"
    after_path = f"after_{uuid.uuid4().hex}.jpg"

    try:
        file1 = request.files.get('before')
        file2 = request.files.get('after')

        if not file1 or not file2:
            return jsonify({"error": "Missing files"}), 400

        # Save files
        file1.save(before_path)
        file2.save(after_path)

        difference, match_score = compare_images(before_path, after_path)

        # ✅ SAME IMAGE CHECK (FIXED POSITION)
        if difference < 0.05:
            return jsonify({
                "difference": difference,
                "match_score": match_score,
                "status": "no_change"
            })

        # ✅ NORMAL RESPONSE
        return jsonify({
            "difference": difference,
            "match_score": match_score,
            "status": "processed"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        # Cleanup
        if os.path.exists(before_path):
            os.remove(before_path)
        if os.path.exists(after_path):
            os.remove(after_path)
