from main import BenchmarkRun, db
import datetime

def record_fish_detection_data(coco_data, fish_detection_data, environment):
    '''
    Record fish detection data to database
    '''
    pass

    # Record fish detection data to database
    new_test_run = BenchmarkRun.benchmark_run(
        coco_image_id=coco_data['image_id'],
        dev_api_version='v1',
        stage_or_production=environment,
        run_datetime=datetime.now(),
        coco_species_genus=coco_data['scientific_name'],
        dev_api_results_json=fish_detection_data, 
        endpoint_execute_time=0.5
    )

    db.session.add(new_test_run)
    db.session.commit()

    test_results = check_benchmark(coco_data['image_id'])
    print(test_results)

def check_benchmark(coco_image_id):
    record = BenchmarkRun.query.filter_by(coco_image_id=coco_image_id).first()
    if record:
        return jsonify({
            'id': record.id,
            'coco_image_id': record.coco_image_id,
            'dev_api_version': record.dev_api_version,
            'stage_or_production': record.stage_or_production.name,
            'run_datetime': record.run_datetime.isoformat(),
            'coco_species_genus': record.coco_species_genus,
            'dev_api_results_json': record.dev_api_results_json,
            'endpoint_execute_time': record.endpoint_execute_time
        })
    else:
        return jsonify({'message': 'Record not found'}), 404

