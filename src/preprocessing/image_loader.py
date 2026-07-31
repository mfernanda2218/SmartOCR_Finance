from typing import Union, Optional, Tuple, Any
import cv2
import numpy as np
from pathlib import Path

from utils.logger import log


class ImageLoader:
    """
    Classe utilitária para leitura, salvamento e validação de imagens.
    """

    @staticmethod
    def load_image(file_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        Carrega uma imagem a partir de um arquivo no disco.

        Args:
            file_path: Caminho para o arquivo da imagem.

        Returns:
            Um array numpy (imagem carregada em BGR) ou None em caso de falha.
        """
        path = Path(file_path)
        if not path.is_file():
            log.error(f"Arquivo de imagem não encontrado: {path}")
            return None

        try:
            # cv2.imread lê a imagem como numpy array BGR
            image = cv2.imread(str(path))
            if image is None:
                log.error(f"Falha ao decodificar a imagem: {path}")
                return None
            
            log.debug(f"Imagem carregada com sucesso: {path} | Formato: {image.shape}")
            return image
        except Exception as e:
            log.exception(f"Erro inesperado ao carregar imagem {path}: {e}")
            return None

    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Carrega uma imagem a partir de um array de bytes (útil para APIs onde o upload não salva em disco imediatamente).

        Args:
            image_bytes: Array de bytes representando a imagem.

        Returns:
            Um array numpy (imagem carregada em BGR) ou None em caso de falha.
        """
        try:
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if image is None:
                log.error("Falha ao decodificar imagem a partir de bytes.")
                return None
                
            log.debug(f"Imagem carregada de bytes com sucesso. | Formato: {image.shape}")
            return image
        except Exception as e:
            log.exception(f"Erro inesperado ao decodificar bytes: {e}")
            return None

    @staticmethod
    def save_image(image: np.ndarray, save_path: Union[str, Path]) -> bool:
        """
        Salva uma imagem (numpy array) no disco.

        Args:
            image: A imagem em formato numpy array (BGR).
            save_path: O caminho de destino.

        Returns:
            True se salvo com sucesso, False caso contrário.
        """
        path = Path(save_path)
        try:
            # Cria o diretório pai caso não exista
            path.parent.mkdir(parents=True, exist_ok=True)
            
            success = cv2.imwrite(str(path), image)
            if success:
                log.debug(f"Imagem salva com sucesso: {path}")
            else:
                log.error(f"Falha ao salvar a imagem usando OpenCV: {path}")
                
            return success
        except Exception as e:
            log.exception(f"Erro inesperado ao salvar imagem em {path}: {e}")
            return False

    @staticmethod
    def validate_image(image: Any) -> bool:
        """
        Verifica se o numpy array provido é uma imagem válida e não vazia.

        Args:
            image: Imagem para validar.

        Returns:
            True se for válida, False caso contrário.
        """
        if not isinstance(image, np.ndarray):
            log.warning("O objeto fornecido não é um numpy array.")
            return False
            
        if image.size == 0:
            log.warning("A imagem está vazia (size == 0).")
            return False
            
        if len(image.shape) < 2:
            log.warning("A imagem não possui dimensões suficientes (mínimo 2D).")
            return False
            
        return True
