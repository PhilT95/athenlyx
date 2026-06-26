from plugin import postprocess_site

if __name__ == "__main__":
    postprocess_site(
        site_dir="site",  # Your build output directory
        docs_dir="docs",  # Your source docs directory
        site_url="https://athenlyx.com",
        default_image="https://athenlyx.com/assets/icon_round.png",
        default_author="docs@s-guard.simplelogin.com",
        add_desc=True,
        add_image=True,
        add_authors=True,
        add_json_ld=True,
        add_css=True,
        verbose=True,
    )