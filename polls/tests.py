import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


""" Model file Testing """


class QuestionModelTests(TestCase):
    # future question pub_date = +30
    def test_was_published_recently_with_future_question_30(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    # future question pub_date = +1
    def test_was_published_recently_with_future_question_1(self):
        time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    # past question pub_date = -1
    def test_was_published_recently_with_past_question_n1(self):
        time = timezone.now() - datetime.timedelta(days=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    # recent question pub_date
    def test_was_published_recently_with_recent_question_1second(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)

    # recent question pub_date = 0
    def test_was_published_recently_with_recent_question_0day(self):
        time = timezone.now() - datetime.timedelta(days=0)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)


""" View File Testing """


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


# testing IndexView()
class QuestionIndexViewTests(TestCase):
    def test_no_questions_with_no_choices(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No question added yet")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question_with_choices(self):
        q1 = create_question(question_text="Past question?", days=-30)
        q1.choice_set.create(choice_text="choice_one", votes=0)
        q1.choice_set.create(choice_text="choice_two", votes=0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [
            '<Question: Past question?>'
        ])

    def test_future_question_with_choices(self):
        q1 = create_question(question_text="Future question?", days=+1)
        q1.choice_set.create(choice_text="choice_one", votes=0)
        q1.choice_set.create(choice_text="choice_two", votes=0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_and_past_question_with_choices(self):
        q1 = create_question(question_text="Future question?", days=+15)
        q1.choice_set.create(choice_text="choice_one", votes=0)
        q1.choice_set.create(choice_text="choice_two", votes=0)
        q2 = create_question(question_text="Past question?", days=-15)
        q2.choice_set.create(choice_text="choice_one", votes=0)
        q2.choice_set.create(choice_text="choice_two", votes=0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [
            '<Question: Past question?>'
        ])

    def test_two_past_question_with_choices(self):
        q1 = create_question(question_text="Past question 1?", days=-2)
        q1.choice_set.create(choice_text="choice_one", votes=0)
        q1.choice_set.create(choice_text="choice_two", votes=0)
        q2 = create_question(question_text="Past question 2?", days=-15)
        q2.choice_set.create(choice_text="choice_one", votes=0)
        q2.choice_set.create(choice_text="choice_two", votes=0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [
            '<Question: Past question 1?>', '<Question: Past question 2?>'
        ])

    # testing questions with no choices won't get published
    def test_question_with_no_choices(self):
        create_question(question_text="Question 1 With no choices?",
                        days=-5)
        create_question(question_text="Question 2 With no choices?",
                        days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    # testing questions with choices will get published
    def test_question_with_choices(self):
        q1 = create_question(question_text="Question 1 With choices?",
                             days=0)
        q1.choice_set.create(choice_text="choice_one", votes=0)
        q1.choice_set.create(choice_text="choice_two", votes=0)
        q2 = create_question(question_text="Question 2 With choices?",
                             days=0)
        q2.choice_set.create(choice_text="choice_one", votes=0)
        q2.choice_set.create(choice_text="choice_two", votes=0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [
            "<Question: Question 2 With choices?>", "<Question: Question 1 With choices?>"
        ])

    # testing question with choices will get published
    # and other won't get published
    def test_question_with_choices_and_other_with_no(self):
        q1 = create_question(question_text="Question 1 With choices?",
                             days=-5)
        q1.choice_set.create(choice_text="choice_one", votes=0)
        q1.choice_set.create(choice_text="choice_two", votes=0)
        create_question(question_text="Question 2 With no choices?",
                        days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [
            "<Question: Question 1 With choices?>"
        ])


# testing DetailView()
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text="Future question?",
                                          days=+2)
        response = self.client.get(reverse("polls:detail", args=(future_question.id, )))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text="Past_question?",
                                        days=-2)
        response = self.client.get(reverse("polls:detail", args=(past_question.pk, )))
        self.assertContains(response, past_question.question_text)


# testing ResultsView()
class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text="Future question?",
                                          days=+2)
        response = self.client.get(reverse("polls:results", args=(future_question.id, )))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text="Past_question?",
                                        days=-2)
        response = self.client.get(reverse("polls:results", args=(past_question.pk, )))
        self.assertContains(response, past_question.question_text)
