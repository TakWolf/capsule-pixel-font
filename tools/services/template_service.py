import bs4
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from tools import configs
from tools.configs import path_define
from tools.services.font_service import DesignContext

_environment = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(path_define.templates_dir),
)


def _make_html(template_name: str, file_name: str, params: dict[str, object] | None = None):
    params = {} if params is None else dict(params)
    params['font_configs'] = configs.font_configs
    params['locale_to_language_flavor'] = configs.locale_to_language_flavor

    html = _environment.get_template(template_name).render(params)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath(file_name)
    file_path.write_text(html, 'utf-8')
    logger.info("Make html: '{}'", file_path)


def make_alphabet_html(design_context: DesignContext):
    _make_html('alphabet.html', f'alphabet-{design_context.font_size}px.html', {
        'font_config': configs.font_configs[design_context.font_size],
        'alphabet': ''.join(sorted(c for c in design_context.alphabet if ord(c) >= 128)),
    })


def _handle_demo_html_element(alphabet: set[str], soup: bs4.BeautifulSoup, element: bs4.PageElement):
    if isinstance(element, bs4.element.Tag):
        for child_element in list(element.contents):
            _handle_demo_html_element(alphabet, soup, child_element)
    elif isinstance(element, bs4.element.NavigableString):
        text = str(element)
        tmp_parent = soup.new_tag('div')
        last_status = False
        text_buffer = ''
        for c in text:
            if c == ' ':
                status = last_status
            elif c == '\n':
                status = True
            else:
                status = c in alphabet
            if last_status != status:
                if text_buffer != '':
                    if last_status:
                        tmp_child = bs4.element.NavigableString(text_buffer)
                    else:
                        tmp_child = soup.new_tag('span')
                        tmp_child.string = text_buffer
                        tmp_child['class'] = f'char-notdef'
                    tmp_parent.append(tmp_child)
                    text_buffer = ''
                last_status = status
            text_buffer += c
        if text_buffer != '':
            if last_status:
                tmp_child = bs4.element.NavigableString(text_buffer)
            else:
                tmp_child = soup.new_tag('span')
                tmp_child.string = text_buffer
                tmp_child['class'] = f'char-notdef'
            tmp_parent.append(tmp_child)
        element.replace_with(tmp_parent)
        tmp_parent.unwrap()


def make_demo_html(design_context: DesignContext):
    content_html = path_define.templates_dir.joinpath('demo-content.html').read_text('utf-8')
    soup = bs4.BeautifulSoup(content_html, 'html.parser')
    _handle_demo_html_element(design_context.alphabet, soup, soup)
    content_html = str(soup).strip()

    _make_html('demo.html', f'demo-{design_context.font_size}px.html', {
        'font_config': configs.font_configs[design_context.font_size],
        'content_html': content_html,
    })


def make_index_html():
    _make_html('index.html', 'index.html')


def make_playground_html():
    _make_html('playground.html', 'playground.html')
