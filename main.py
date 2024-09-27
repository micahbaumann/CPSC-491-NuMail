from server.server import *


# Main Code
if __name__ == "__main__":
    try:
        argparser = argparse.ArgumentParser()
        argparser.add_argument("-c", "--config")
        runtime_args = argparser.parse_args()

        if runtime_args.config:
            config_path = Path(runtime_args.config)
            if config_path.exists():
                server_config(config_path)
            else:
                raise NuMailError(code="7.1.1", message=f"Error opening config file \"{config_path.resolve()}\"")
        else:
            config_path = Path(__file__).parent.parent / "config" / "settings.conf"
            if config_path.exists():
                server_config(config_path.resolve())

        

        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("Server stopped.")
        server_log.log("Server stopped")
    except NuMailError as e:
        print(e)
        server_log.log(e, type="error")
    except Exception as e:
        print(f"An error has occurred:\n{e}")
        server_log.log(f"An error has occurred:\n{e}", type="error")