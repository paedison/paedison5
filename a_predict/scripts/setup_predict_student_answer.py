import csv

from a_predict.models import Student, StudentAnswer, SubmittedAnswer


def write_csv(filename, fieldnames, rows):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csv_file:
        csvwriter = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csvwriter.writeheader()
        for row in rows:
            csvwriter.writerow(row)
    print(f'Successfully written in f{filename}')


def run():
    students = Student.objects.all()
    subject_list = {
        '헌법': 'heonbeob',
        '언어': 'eoneo',
        '자료': 'jaryo',
        '상황': 'sanghwang',
    }
    for student in students:
        student_answer, created = StudentAnswer.objects.get_or_create(student=student)

        for subject, field in subject_list.items():
            problem_count = 40
            if student.exam == '칠급' or subject == '헌법':
                problem_count = 25

            submitted_answers = SubmittedAnswer.objects.filter(
                student=student, subject=subject
            ).order_by('number').values('number', 'answer')

            answer_count = submitted_answers.count()
            if answer_count == problem_count:
                answer_list = [''] * problem_count
                for ans in submitted_answers:
                    index = ans['number'] - 1
                    answer_list[index] = str(ans['answer'])
                answer_string = ','.join(answer_list)
            else:
                answer_string = ''
            setattr(student_answer, field, answer_string)
            student_answer.save(message_type=field)
