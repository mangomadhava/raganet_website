from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

# from .. import movie_client
from ..forms import  AudioForm, VerifyResultForm, MoreInfoForm
from ..models import User, AudioFile, Accuracy
from ..utils import current_time
import io
import base64
import os
from pydub import AudioSegment
import pydub
from werkzeug.utils import secure_filename
from ..client import *

model = Blueprint("model", __name__)


@model.route("/", methods=["GET", "POST"])
def index():
    acc_object = Accuracy.objects()[0]
    formatter = "{0:.2f}"
    acc = acc_object.correct / (acc_object.num_tries + 10e-10)
    acc = float(acc) * 100
    acc = formatter.format(acc)
    acc = str(acc)
    return render_template("index.html", acc = acc)

@model.route("/info", methods = ["GET", "POST"])
def info():
    more_info = MoreInfoForm()
    if more_info.validate_on_submit():
        return redirect(more_info.choose_raga.data)
    return render_template("info.html", more_info = more_info)


@model.route("/prediction", methods = ["GET", "POST"])
def prediction():
    form = AudioForm()
    result_form = VerifyResultForm()
    if form.validate_on_submit():
        a = form.audio.data
        filename = secure_filename(a.filename)
        content_type = f'audio/{filename[-3:]}'
        print(content_type == 'audio/mp3')
        if content_type != 'audio/mp3':
            flash('Please Upload An .mp3 File!')
            return redirect(url_for("model.prediction"))

        audio_obj = AudioFile()
        audio_obj.audio.put(a.stream, content_type = content_type)


        bytes_im = io.BytesIO(audio_obj.audio.read())
        audio_encoded = base64.b64encode(bytes_im.getvalue()).decode()

        try:
            recording = AudioSegment.from_file(bytes_im, format="mp3")
        except pydub.exceptions.CouldntDecodeError:
            flash('FFMPEG could not decode this audio. Please try a different mp3. ')
            return redirect(url_for("model.prediction"))
        filename = './temp/' + current_time() + '.mp3'
        recording.export(filename, format='mp3')
        try:
            raga_name_predicted = predict(filename)
        except:
            flash('Something went wrong! Try again with an audio clip of at least 30 seconds.')
            os.remove(filename)
            return redirect(url_for("model.prediction"))
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
