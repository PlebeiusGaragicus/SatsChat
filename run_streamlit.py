if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    # import logging
    # logging.getLogger("fsevents").setLevel(logging.WARNING)
    # logging.getLogger("PIL").setLevel(logging.WARNING)
    # logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    # logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("langsmith.client").setLevel(logging.WARNING)
    # logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    # logging.getLogger("httpcore.connection").setLevel(logging.WARNING)

    # from src.interface.login import login_router_page
    # login_router_page()

    from src.main import main
    main()
