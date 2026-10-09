"""
Model exported as python.
Name : Analiza_15m
Group : Miasto15m
With QGIS : 33203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Analiza_15m(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('granica_miasta', 'Granica miasta', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('poi_edukacja', 'POI Edukacja', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('poi_handel', 'POI Handel', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('poi_transport', 'POI Transport', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('poi_zdrowie', 'POI Zdrowie', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('poi_ziele', 'POI Zieleń', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('waga_edukacja', 'waga_edukacja', type=QgsProcessingParameterNumber.Double, defaultValue=3))
        self.addParameter(QgsProcessingParameterNumber('waga_handel', 'waga_handel', type=QgsProcessingParameterNumber.Double, defaultValue=2))
        self.addParameter(QgsProcessingParameterNumber('waga_transport', 'waga_transport', type=QgsProcessingParameterNumber.Double, defaultValue=1))
        self.addParameter(QgsProcessingParameterNumber('waga_zdrowie', 'waga_zdrowie', type=QgsProcessingParameterNumber.Double, defaultValue=3))
        self.addParameter(QgsProcessingParameterNumber('waga_ziele', 'waga_zieleń', type=QgsProcessingParameterNumber.Double, defaultValue=2))
        self.addParameter(QgsProcessingParameterFeatureSink('Siatka_analiza_15m', 'siatka_analiza_15m', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(12, model_feedback)
        results = {}
        outputs = {}

        # Utwórz siatkę
        alg_params = {
            'CRS': 'ProjectCrs',
            'EXTENT': parameters['granica_miasta'],
            'HOVERLAY': 0,
            'HSPACING': 250,
            'TYPE': 4,  # Sześciokąt (poligon)
            'VOVERLAY': 0,
            'VSPACING': 250,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['UtwrzSiatk'] = processing.run('native:creategrid', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Przytnij
        alg_params = {
            'INPUT': outputs['UtwrzSiatk']['OUTPUT'],
            'OVERLAY': parameters['granica_miasta'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Przytnij'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Centroidy
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['Przytnij']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroidy'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Bufory wektorowe
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 1000,
            'EXPLODE_COLLECTIONS': False,
            'FIELD': '',
            'GEOMETRY': 'geom',
            'INPUT': outputs['Centroidy']['OUTPUT'],
            'OPTIONS': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BuforyWektorowe'] = processing.run('gdal:buffervectors', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Policz punkty w poligonie - Edukacja
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'cnt_edukacja',
            'POINTS': parameters['poi_edukacja'],
            'POLYGONS': outputs['BuforyWektorowe']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoliczPunktyWPoligonieEdukacja'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Policz punkty w poligonie - Zdrowie
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'cnt_zdrowie',
            'POINTS': parameters['poi_zdrowie'],
            'POLYGONS': outputs['PoliczPunktyWPoligonieEdukacja']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoliczPunktyWPoligonieZdrowie'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Policz punkty w poligonie - Handel
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'cnt_handel',
            'POINTS': parameters['poi_handel'],
            'POLYGONS': outputs['PoliczPunktyWPoligonieZdrowie']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoliczPunktyWPoligonieHandel'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Policz punkty w poligonie - Zieleń
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'cnt_zielen',
            'POINTS': parameters['poi_ziele'],
            'POLYGONS': outputs['PoliczPunktyWPoligonieHandel']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoliczPunktyWPoligonieZiele'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Policz punkty w poligonie - Transport
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'cnt_transport',
            'POINTS': parameters['poi_transport'],
            'POLYGONS': outputs['PoliczPunktyWPoligonieZiele']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoliczPunktyWPoligonieTransport'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Kalkulator pól
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'index_15m',
            'FIELD_PRECISION': 1,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '(\r\n  (IF("cnt_edukacja" > 0, 1, 0) * @waga_edukacja) +\r\n  (IF("cnt_zdrowie" > 0, 1, 0) * @waga_zdrowie) +\r\n  (IF("cnt_handel" > 0, 1, 0) * @waga_handel) +\r\n  (IF("cnt_zielen" > 0, 1, 0) * @waga_zielen) +\r\n  (IF("cnt_transport" > 0, 1, 0) * @waga_transport)\r\n) / (@waga_edukacja + @waga_zdrowie + @waga_handel + @waga_zielen + @waga_transport) * 100.0',
            'INPUT': outputs['PoliczPunktyWPoligonieTransport']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KalkulatorPl'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Kalkulator pól bonus
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'index_15m_bonus',
            'FIELD_PRECISION': 1,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '(\r\n  (min("cnt_edukacja", 3) * @waga_edukacja) +\r\n  (min("cnt_zdrowie", 3) * @waga_zdrowie) +\r\n  (min("cnt_handel", 3) * @waga_handel) +\r\n  (min("cnt_zielen", 3) * @waga_zielen) +\r\n  (min("cnt_transport", 3) * @waga_transport)\r\n) / ((@waga_edukacja + @waga_zdrowie + @waga_handel + @waga_zielen + @waga_transport) * 3.0) * 100.0',
            'INPUT': outputs['KalkulatorPl']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KalkulatorPlBonus'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Złącz atrybuty według wartości pola
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'id',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'id',
            'INPUT': outputs['Przytnij']['OUTPUT'],
            'INPUT_2': outputs['KalkulatorPlBonus']['OUTPUT'],
            'METHOD': 1,  # przyjmuj atrybuty tylko z pierwszego pasującego obiektu (jeden do jednego)
            'PREFIX': '',
            'OUTPUT': parameters['Siatka_analiza_15m']
        }
        outputs['ZczAtrybutyWedugWartociPola'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Siatka_analiza_15m'] = outputs['ZczAtrybutyWedugWartociPola']['OUTPUT']
        return results

    def name(self):
        return 'Analiza_15m'

    def displayName(self):
        return 'Analiza_15m'

    def group(self):
        return 'Miasto15m'

    def groupId(self):
        return 'Miasto15m'

    def createInstance(self):
        return Analiza_15m()
