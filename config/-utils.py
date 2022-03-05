
import pprint
import json

from django.utils.html import strip_tags
from django.core import mail
from django.core.validators import validate_ipv46_address

from django.conf import settings
from django.template import Context, Template


from django.core.mail import EmailMultiAlternatives  # send_mail

from django.template.loader import render_to_string

from config.logger import logger

site_dict = {
    'site': {
        'id': settings.SITE_ID,
        'name': 'sapé',
        'url': 'https://shopsape.com',
        'url_display': 'shopsape.com',
        'email': settings.DEFAULT_FROM_EMAIL,

        'debug': settings.DEBUG,
        # 'is_sandbox': settings.IS_SANDBOX,

    },
    'social': {
        'instagram': {
            'username': 'shopsapeonline',
            'url': 'https://instagram.com/shopsapeonline'
        },

        'facebook': '',
        'pinterest': ''
    }
}


def get_ip(request):
    ip = '127.0.0.1'
    try:
        ip = request.META.get(
            'HTTP_X_FORWARDED_FOR',
            request.META.get('REMOTE_ADDR', '127.0.0.1'))
        validate_ipv46_address(ip)
    except Exception as e:
        print(e)
    return ip


def render(content, context={}):
    context.update(site_dict)

    t = Template(str(content))
    return t.render(Context(context))


def send_mass_html_email(subject, from_email, to_list, content, context={}):
    if not isinstance(to_list, tuple) and not isinstance(to_list, list):
        raise TypeError('to list must be tuple or a list')

    sent = False
    i = len(to_list)

    logger.debug(
        f'Sending mass emails: '
        f'from {from_email} to {i} recipients. Status: {sent}')

    try:
        i = 0
        connection = mail.get_connection()
        opened = connection.open()
        logger.info(f'Connection Opnened: {opened}')

        for email in to_list:
            _sent = send_html_email(
                subject, from_email, email,
                content, context=context)

            if _sent:
                i += 1

    except Exception as e:
        logger.error(f'Could not send mass emails.\n{e}')

    else:
        sent = True
    finally:
        connection.close()
        logger.info(f'{i} emails sent. Connection closed. Status: {sent}')
        return sent


def send_html_email(subject, from_email, to_list, content, context={}):
    # context.update(site_dict)

    logger.debug('Sending html email.')

    t = Template(content)
    html_content = t.render(Context(context))
    text_content = strip_tags(html_content)

    if not isinstance(to_list, list) or not isinstance(to_list, tuple):
        to_list = [to_list]

    try:
        m = EmailMultiAlternatives(
            subject, text_content, from_email=from_email, to=to_list)
        m.attach_alternative(html_content, "text/html")
    except Exception as e:
        logger.error('Error sending mail', exc_info=1)
        logger.error('Could not send email to {}'.format(to_list[0]))
    else:
        m.send()
        return True

    return False


def send_html_email_from_file(
    subject, from_email, to_list, email_template,
        context={}):

    context.update(site_dict)
    html_content = render_to_string(email_template, context)
    text_content = strip_tags(html_content)
    try:
        m = EmailMultiAlternatives(
            subject, text_content, from_email=from_email, to=to_list)
        m.attach_alternative(html_content, "text/html")
    except Exception as e:
        logger.error('Error sending mail', exc_info=1)
    else:
        m.send()


def send_mail(
    subject, from_email, to_list,
    text_content, html_content=None,
        fail=True):

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_list)
    if html_content:
        msg.attach_alternative(html_content, 'text/html')
    msg.send()


def jprint(data, name=None):
    print('\n- JPRINTING {} - '.format(
        '' if not name else name.upper()))
    try:
        if isinstance(data, dict):
            print(json.dumps(data, indent=4))
        elif isinstance(data, list) or isinstance(data, set):
            print('[')
            for i in data:
                print('{}'.format(' ' * 2), i, sep=' ')
            print(']')
    except Exception as e:
        try:
            pprint.pprint(data)
        except Exception as e:
            print(data)
    finally:
        print(' *--* ' * 4, '\n')
