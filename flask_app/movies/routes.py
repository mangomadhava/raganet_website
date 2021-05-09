from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

# from .. import movie_client
from ..forms import  AudioForm, VerifyResultForm
from ..models import User, AudioFile, Accuracy
from ..utils import current_time
import io
import base64
import os
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from ..client import *

model = Blueprint("model", __name__)


@model.route("/", methods=["GET", "POST"])
def index():
    acc_object = Accuracy.objects()[0]
    formatter = "{0:.2f}"
    acc = acc_object.correct / (acc_object.num_tries + 10e-10)
    acc = formatter.format(acc)
    return render_template("index.html", acc = acc)


@model.route("/prediction", methods = ["GET", "POST"])
def prediction():
    form = AudioForm()
    result_form = VerifyResultForm()
    # acc_object = Accuracy.objects()
    # print(len(acc_object))
    # acc_object = acc_object[0]
    # print(acc_object.num_tries, acc_object.correct)

    if form.validate_on_submit():
        a = form.audio.data
        filename = secure_filename(a.filename)
        content_type = f'audio/{filename[-3:]}'
        audio_obj = AudioFile()
        audio_obj.audio.put(a.stream, content_type = content_type)


        bytes_im = io.BytesIO(audio_obj.audio.read())
        audio_encoded = base64.b64encode(bytes_im.getvalue()).decode()


        recording = AudioSegment.from_file(bytes_im, format="mp3")
        filename = './temp/' + current_time() + '.mp3'
        recording.export(filename, format='mp3')

        raga_name_predicted = predict(filename)
        os.remove(filename)

        if current_user.is_authenticated:
            c_user = current_user._get_current_object()
            all_audios = AudioFile.objects(user=c_user)
            if len(all_audios) > 4:
                to_delete = all_audios[0]
                to_delete.delete()

            audio_obj.user = current_user._get_current_object()
            audio_obj.prediction = raga_name_predicted
            audio_obj.truth = form.actual.data
            audio_obj.save()

        return render_template("prediction.html", form = form, audio_encoded = audio_encoded, predicted = raga_name_predicted, result_form = result_form)

    if result_form.validate_on_submit():
        acc_object = Accuracy.objects()[0]
        if result_form.result.data == "Correct":
            acc_object.correct = acc_object.correct + 1
        acc_object.num_tries = acc_object.num_tries + 1
        acc_object.save()
        return redirect(url_for("model.index"))

    return render_template("prediction.html", form = form)
#
# @model.route("/search-results/<query>", methods=["GET"])
# def query_results(query):
#     try:
#         results = movie_client.search(query)
#     except ValueError as e:
#         flash(str(e))
#         return redirect(url_for("movies.index"))
#
#     return render_template("query.html", results=results)
#
#
# @model.route("/movies/<movie_id>", methods=["GET", "POST"])
# def movie_detail(movie_id):
#     try:
#         result = movie_client.retrieve_movie_by_id(movie_id)
#     except ValueError as e:
#         flash(str(e))
#         return redirect(url_for("users.login"))
#
#     form = MovieReviewForm()
#     if form.validate_on_submit() and current_user.is_authenticated:
#         review = Review(
#             commenter=current_user._get_current_object(),
#             content=form.text.data,
#             date=current_time(),
#             imdb_id=movie_id,
#             movie_title=result.title,
#         )
#         review.save()
#
#         return redirect(request.path)
#
#     reviews = Review.objects(imdb_id=movie_id)
#
#     return render_template(
#         "movie_detail.html", form=form, movie=result, reviews=reviews
#     )
