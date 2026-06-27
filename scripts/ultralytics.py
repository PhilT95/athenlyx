from plugin import postprocess_site

if __name__ == "__main__":
    postprocess_site(
        site_dir="site",
        docs_dir="docs",
        site_url="https://athenlyx.com",
        default_image="https://athenlyx.com/assets/icon_round.png",
        default_author="41484279+PhilT95@users.noreply.github.com",
        add_desc=True,
        add_image=True,
        add_keywords=True,
        add_authors=True,
        add_json_ld=True,
        add_share_buttons=False,
        add_css=True,
        verbose=True,
    )